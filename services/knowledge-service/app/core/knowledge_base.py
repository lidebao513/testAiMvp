from typing import List, Dict, Any, Optional
import pymongo
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import openai
import requests
import json

class KnowledgeBase:
    """知识库类，用于存储和管理测试相关的知识
    
    该类提供了存储缺陷、测试模式和最佳实践的功能，并支持基于向量的相似性搜索。
    
    Args:
        mongo_uri (str): MongoDB连接URI
        milvus_uri (str): Milvus向量数据库连接URI
    """
    
    def __init__(self, mongo_uri: str, milvus_uri: str, openai_api_key: Optional[str] = None, embedding_model: str = "text-embedding-ada-002", local_embedding_url: Optional[str] = None):
        """初始化知识库
        
        连接MongoDB和Milvus，初始化集合和向量库。
        
        Args:
            mongo_uri (str): MongoDB连接URI
            milvus_uri (str): Milvus向量数据库连接URI
            openai_api_key (Optional[str], optional): OpenAI API密钥，默认为None
            embedding_model (str, optional): 嵌入模型，默认为"text-embedding-ada-002"
            local_embedding_url (Optional[str], optional): 本地嵌入模型API地址，默认为None
        """
        # 初始化嵌入模型配置
        self.openai_api_key = openai_api_key
        self.embedding_model = embedding_model
        self.local_embedding_url = local_embedding_url
        
        # 尝试连接MongoDB
        try:
            # 连接MongoDB
            self.mongo_client = pymongo.MongoClient(mongo_uri)
            self.db = self.mongo_client["ai_test_engineer"]
            
            # 初始化集合
            self.defects_collection = self.db["defects"]  # 缺陷集合
            self.test_patterns_collection = self.db["test_patterns"]  # 测试模式集合
            self.best_practices_collection = self.db["best_practices"]  # 最佳实践集合
            self.test_cases_collection = self.db["test_cases"]  # 测试用例集合
            self.defect_patterns_collection = self.db["defect_patterns"]  # 缺陷模式集合
            print("MongoDB连接成功")
        except Exception as e:
            print(f"MongoDB连接失败: {str(e)}")
            # 创建内存中的集合作为备用
            self.defects_collection = []
            self.test_patterns_collection = []
            self.best_practices_collection = []
            self.test_cases_collection = []
            self.defect_patterns_collection = []
            print("知识库服务将在内存模式下运行，数据不会持久化")
        
        # 暂时不尝试连接Milvus，直接设置为未连接状态
        self.milvus_connected = False
        print("Milvus连接被跳过，某些功能可能不可用")
        # 注释掉Milvus连接代码，避免初始化时出错
        # try:
        #     # 确保Milvus URI格式正确，添加tcp://协议前缀
        #     if not milvus_uri.startswith(('unix:', 'http:', 'https:', 'tcp:')):
        #         milvus_uri = f"tcp://{milvus_uri}"
        #     connections.connect("default", uri=milvus_uri)
        #     # 初始化Milvus向量库
        #     self._init_milvus_collection()
        #     self.milvus_connected = True
        #     print("Milvus连接成功")
        # except Exception as e:
        #     print(f"Milvus连接失败: {str(e)}")
        #     print("知识库服务将在没有Milvus的情况下运行，某些功能可能不可用")
    
    def _init_milvus_collection(self):
        """初始化Milvus向量库
        
        创建或获取Milvus集合，用于存储和搜索向量数据。
        """
        try:
            # 定义向量库字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),  # 主键字段
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),  # 向量字段，维度为768
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),  # 内容字段，增加长度
                FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=50),  # 类型字段
                FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=5000)  # 元数据字段
            ]
            
            # 创建集合 schema
            schema = CollectionSchema(fields, "AI Test Engineer Knowledge Base")
            
            # 创建或获取集合
            try:
                # 尝试获取已存在的集合
                self.milvus_collection = Collection("knowledge_base", schema)
            except:
                # 如果集合不存在，创建新集合
                self.milvus_collection = Collection.create("knowledge_base", schema)
            
            # 创建索引以提高搜索性能
            index_params = {
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128}
            }
            try:
                self.milvus_collection.create_index("embedding", index_params)
            except:
                pass  # 索引已存在
            
            # 加载集合到内存
            self.milvus_collection.load()
        except Exception as e:
            print(f"初始化Milvus集合失败: {str(e)}")
            self.milvus_connected = False
    
    def add_defect(self, defect: Dict[str, Any]) -> str:
        """添加缺陷到知识库
        
        将缺陷信息添加到MongoDB的defects集合中，并生成嵌入向量存储到Milvus（如果Milvus连接成功）。
        
        Args:
            defect (Dict[str, Any]): 缺陷信息
            
        Returns:
            str: 缺陷ID
            
        Example:
            >>> kb = KnowledgeBase(mongo_uri="mongodb://localhost:27017", milvus_uri="localhost:19530")
            >>> defect = {"title": "登录失败", "description": "用户输入正确密码但登录失败", "severity": "High"}
            >>> defect_id = kb.add_defect(defect)
            >>> print(defect_id)
            "5f7a1b2c3d4e5f6g7h8i9j0k"
        """
        # 插入缺陷到MongoDB
        result = self.defects_collection.insert_one(defect)
        defect_id = str(result.inserted_id)
        
        # 如果Milvus连接成功，生成并存储嵌入向量
        if self.milvus_connected:
            try:
                # 生成缺陷的文本表示
                defect_text = f"{defect.get('title', '')} {defect.get('description', '')} {defect.get('severity', '')}"
                
                # 生成嵌入向量
                embedding = self.generate_embedding(defect_text)
                
                # 存储到Milvus
                metadata = json.dumps({
                    "defect_id": defect_id,
                    "type": "defect",
                    "severity": defect.get("severity", "")
                })
                
                self.milvus_collection.insert([
                    embedding,
                    defect_text,
                    "defect",
                    metadata
                ])
            except Exception as e:
                print(f"存储缺陷向量失败: {str(e)}")
        
        return defect_id
    
    def get_defects(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取缺陷列表
        
        从MongoDB的defects集合中获取缺陷列表，支持过滤条件。
        
        Args:
            filters (Dict[str, Any], optional): 过滤条件，默认为None
            
        Returns:
            List[Dict[str, Any]]: 缺陷列表
            
        Example:
            >>> kb = KnowledgeBase(mongo_uri="mongodb://localhost:27017", milvus_uri="localhost:19530")
            >>> defects = kb.get_defects({"severity": "High"})
            >>> print(len(defects))
            5
        """
        query = filters or {}
        return list(self.defects_collection.find(query))
    
    def add_test_pattern(self, pattern: Dict[str, Any]) -> str:
        """添加测试模式到知识库
        
        将测试模式信息添加到MongoDB的test_patterns集合中。
        
        Args:
            pattern (Dict[str, Any]): 测试模式信息
            
        Returns:
            str: 测试模式ID
            
        Example:
            >>> kb = KnowledgeBase(mongo_uri="mongodb://localhost:27017", milvus_uri="localhost:19530")
            >>> pattern = {"name": "边界值测试", "description": "测试边界条件", "category": "单元测试"}
            >>> pattern_id = kb.add_test_pattern(pattern)
            >>> print(pattern_id)
            "5f7a1b2c3d4e5f6g7h8i9j0k"
        """
        # 插入测试模式到MongoDB
        result = self.test_patterns_collection.insert_one(pattern)
        return str(result.inserted_id)
    
    def get_test_patterns(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取测试模式列表
        
        从MongoDB的test_patterns集合中获取测试模式列表，支持过滤条件。
        
        Args:
            filters (Dict[str, Any], optional): 过滤条件，默认为None
            
        Returns:
            List[Dict[str, Any]]: 测试模式列表
            
        Example:
            >>> kb = KnowledgeBase(mongo_uri="mongodb://localhost:27017", milvus_uri="localhost:19530")
            >>> patterns = kb.get_test_patterns({"category": "单元测试"})
            >>> print(len(patterns))
            10
        """
        query = filters or {}
        return list(self.test_patterns_collection.find(query))
    
    def add_best_practice(self, practice: Dict[str, Any]) -> str:
        """添加最佳实践到知识库
        
        将最佳实践信息添加到MongoDB的best_practices集合中。
        
        Args:
            practice (Dict[str, Any]): 最佳实践信息
            
        Returns:
            str: 最佳实践ID
            
        Example:
            >>> kb = KnowledgeBase(mongo_uri="mongodb://localhost:27017", milvus_uri="localhost:19530")
            >>> practice = {"title": "测试命名规范", "description": "测试方法名应清晰表达测试目的", "category": "测试规范"}
            >>> practice_id = kb.add_best_practice(practice)
            >>> print(practice_id)
            "5f7a1b2c3d4e5f6g7h8i9j0k"
        """
        # 插入最佳实践到MongoDB
        result = self.best_practices_collection.insert_one(practice)
        return str(result.inserted_id)
    
    def get_best_practices(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取最佳实践列表
        
        从MongoDB的best_practices集合中获取最佳实践列表，支持过滤条件。
        
        Args:
            filters (Dict[str, Any], optional): 过滤条件，默认为None
            
        Returns:
            List[Dict[str, Any]]: 最佳实践列表
            
        Example:
            >>> kb = KnowledgeBase(mongo_uri="mongodb://localhost:27017", milvus_uri="localhost:19530")
            >>> practices = kb.get_best_practices({"category": "测试规范"})
            >>> print(len(practices))
            8
        """
        query = filters or {}
        return list(self.best_practices_collection.find(query))
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似的知识
        
        在Milvus向量库中搜索与查询向量相似的知识（如果Milvus连接成功）。
        
        Args:
            query_embedding (List[float]): 查询向量
            top_k (int, optional): 返回结果数量，默认为5
            
        Returns:
            List[Dict[str, Any]]: 相似知识列表，包含ID、距离和内容
            
        Example:
            >>> kb = KnowledgeBase(mongo_uri="mongodb://localhost:27017", milvus_uri="localhost:19530")
            >>> query_vector = [0.1, 0.2, ..., 0.9]  # 768维向量
            >>> similar_items = kb.search_similar(query_vector, top_k=3)
            >>> print(len(similar_items))
            3
        """
        # 如果Milvus连接成功，执行搜索
        if self.milvus_connected:
            try:
                # 定义搜索参数
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}  # 使用L2距离度量
                
                # 执行搜索
                results = self.milvus_collection.search(
                    data=[query_embedding],  # 查询向量
                    anns_field="embedding",  # 向量字段
                    param=search_params,  # 搜索参数
                    limit=top_k,  # 返回结果数量
                    expr=None  # 过滤表达式
                )
                
                # 处理搜索结果
                similar_items = []
                for hits in results:
                    for hit in hits:
                        # 查询完整的内容信息
                        content_info = self.milvus_collection.query(
                            expr=f"id == {hit.id}",
                            output_fields=["content", "type"]
                        )[0]
                        
                        # 构建相似项
                        similar_items.append({
                            "id": hit.id,
                            "distance": hit.distance,  # 距离越小越相似
                            "content": content_info
                        })
                
                return similar_items
            except Exception as e:
                print(f"搜索相似知识失败: {str(e)}")
                return []
        else:
            print("Milvus未连接，无法搜索相似知识")
            return []
    
    def generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量
        
        使用配置的嵌入模型生成文本的向量表示。
        
        Args:
            text (str): 要生成嵌入向量的文本
            
        Returns:
            List[float]: 文本的嵌入向量
        """
        if self.local_embedding_url:
            # 使用本地部署的BGE模型
            try:
                response = requests.post(
                    self.local_embedding_url,
                    json={"input": text},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()["embedding"]
            except Exception as e:
                raise Exception(f"本地嵌入模型调用失败: {str(e)}")
        elif self.openai_api_key:
            # 使用OpenAI的text-embedding-ada-002模型
            try:
                openai.api_key = self.openai_api_key
                response = openai.Embedding.create(
                    model=self.embedding_model,
                    input=text
                )
                return response["data"][0]["embedding"]
            except Exception as e:
                raise Exception(f"OpenAI嵌入模型调用失败: {str(e)}")
        else:
            raise Exception("未配置嵌入模型")
    
    def add_test_case(self, test_case: Dict[str, Any]) -> str:
        """添加测试用例到知识库
        
        将测试用例信息添加到MongoDB的test_cases集合中，并生成嵌入向量存储到Milvus（如果Milvus连接成功）。
        
        Args:
            test_case (Dict[str, Any]): 测试用例信息
            
        Returns:
            str: 测试用例ID
        """
        # 插入测试用例到MongoDB
        result = self.test_cases_collection.insert_one(test_case)
        test_case_id = str(result.inserted_id)
        
        # 如果Milvus连接成功，生成并存储嵌入向量
        if self.milvus_connected:
            try:
                # 生成测试用例的文本表示
                test_case_text = f"{test_case.get('title', '')} {test_case.get('description', '')} {test_case.get('steps', '')}"
                
                # 生成嵌入向量
                embedding = self.generate_embedding(test_case_text)
                
                # 存储到Milvus
                metadata = json.dumps({
                    "test_case_id": test_case_id,
                    "type": "test_case",
                    "category": test_case.get("category", "")
                })
                
                self.milvus_collection.insert([
                    embedding,
                    test_case_text,
                    "test_case",
                    metadata
                ])
            except Exception as e:
                print(f"存储测试用例向量失败: {str(e)}")
        
        return test_case_id
    
    def add_defect_pattern(self, defect_pattern: Dict[str, Any]) -> str:
        """添加缺陷模式到知识库
        
        将缺陷模式信息添加到MongoDB的defect_patterns集合中，并生成嵌入向量存储到Milvus（如果Milvus连接成功）。
        
        Args:
            defect_pattern (Dict[str, Any]): 缺陷模式信息
            
        Returns:
            str: 缺陷模式ID
        """
        # 插入缺陷模式到MongoDB
        result = self.defect_patterns_collection.insert_one(defect_pattern)
        defect_pattern_id = str(result.inserted_id)
        
        # 如果Milvus连接成功，生成并存储嵌入向量
        if self.milvus_connected:
            try:
                # 生成缺陷模式的文本表示
                defect_pattern_text = f"{defect_pattern.get('name', '')} {defect_pattern.get('description', '')} {defect_pattern.get('symptoms', '')}"
                
                # 生成嵌入向量
                embedding = self.generate_embedding(defect_pattern_text)
                
                # 存储到Milvus
                metadata = json.dumps({
                    "defect_pattern_id": defect_pattern_id,
                    "type": "defect_pattern",
                    "category": defect_pattern.get("category", "")
                })
                
                self.milvus_collection.insert([
                    embedding,
                    defect_pattern_text,
                    "defect_pattern",
                    metadata
                ])
            except Exception as e:
                print(f"存储缺陷模式向量失败: {str(e)}")
        
        return defect_pattern_id
    
    def search_similar_test_cases(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索相似的测试用例
        
        在Milvus向量库中搜索与查询文本相似的测试用例（如果Milvus连接成功）。
        
        Args:
            query (str): 查询文本
            top_k (int, optional): 返回结果数量，默认为5
            category (Optional[str], optional): 测试用例类别过滤，默认为None
            
        Returns:
            List[Dict[str, Any]]: 相似测试用例列表
        """
        # 如果Milvus连接成功，执行搜索
        if self.milvus_connected:
            try:
                # 生成查询向量
                query_embedding = self.generate_embedding(query)
                
                # 构建过滤表达式
                expr = "type == 'test_case'"
                if category:
                    expr += f" and metadata like '%category: {category}%'"
                
                # 定义搜索参数
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
                
                # 执行搜索
                results = self.milvus_collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    expr=expr
                )
                
                # 处理搜索结果
                similar_test_cases = []
                for hits in results:
                    for hit in hits:
                        # 查询完整的内容信息
                        content_info = self.milvus_collection.query(
                            expr=f"id == {hit.id}",
                            output_fields=["content", "type", "metadata"]
                        )[0]
                        
                        # 解析元数据
                        metadata = json.loads(content_info["metadata"])
                        
                        # 获取测试用例详细信息
                        test_case = self.test_cases_collection.find_one({"_id": pymongo.ObjectId(metadata["test_case_id"])})
                        if test_case:
                            test_case["_id"] = str(test_case["_id"])
                            similar_test_cases.append({
                                "test_case": test_case,
                                "similarity": 1.0 / (1.0 + hit.distance),  # 将距离转换为相似度
                                "distance": hit.distance
                            })
                
                return similar_test_cases
            except Exception as e:
                print(f"搜索相似测试用例失败: {str(e)}")
                return []
        else:
            print("Milvus未连接，无法搜索相似测试用例")
            return []
    
    def search_similar_defects(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似的缺陷
        
        在Milvus向量库中搜索与查询文本相似的缺陷和缺陷模式（如果Milvus连接成功）。
        
        Args:
            query (str): 查询文本
            top_k (int, optional): 返回结果数量，默认为5
            
        Returns:
            List[Dict[str, Any]]: 相似缺陷列表
        """
        # 如果Milvus连接成功，执行搜索
        if self.milvus_connected:
            try:
                # 生成查询向量
                query_embedding = self.generate_embedding(query)
                
                # 构建过滤表达式
                expr = "type in ['defect', 'defect_pattern']"
                
                # 定义搜索参数
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
                
                # 执行搜索
                results = self.milvus_collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    expr=expr
                )
                
                # 处理搜索结果
                similar_defects = []
                for hits in results:
                    for hit in hits:
                        # 查询完整的内容信息
                        content_info = self.milvus_collection.query(
                            expr=f"id == {hit.id}",
                            output_fields=["content", "type", "metadata"]
                        )[0]
                        
                        # 解析元数据
                        metadata = json.loads(content_info["metadata"])
                        
                        if content_info["type"] == "defect":
                            # 获取缺陷详细信息
                            defect = self.defects_collection.find_one({"_id": pymongo.ObjectId(metadata["defect_id"])})
                            if defect:
                                defect["_id"] = str(defect["_id"])
                                similar_defects.append({
                                    "defect": defect,
                                    "type": "defect",
                                    "similarity": 1.0 / (1.0 + hit.distance),
                                    "distance": hit.distance
                                })
                        elif content_info["type"] == "defect_pattern":
                            # 获取缺陷模式详细信息
                            defect_pattern = self.defect_patterns_collection.find_one({"_id": pymongo.ObjectId(metadata["defect_pattern_id"])})
                            if defect_pattern:
                                defect_pattern["_id"] = str(defect_pattern["_id"])
                                similar_defects.append({
                                    "defect_pattern": defect_pattern,
                                    "type": "defect_pattern",
                                    "similarity": 1.0 / (1.0 + hit.distance),
                                    "distance": hit.distance
                                })
                
                return similar_defects
            except Exception as e:
                print(f"搜索相似缺陷失败: {str(e)}")
                return []
        else:
            print("Milvus未连接，无法搜索相似缺陷")
            return []
    
    def rag_enhanced_generation(self, query: str, context_size: int = 3) -> Dict[str, Any]:
        """检索增强生成 (RAG) 提升测试生成质量
        
        检索与查询相关的知识，作为上下文来增强生成质量（如果Milvus连接成功）。
        
        Args:
            query (str): 查询文本
            context_size (int, optional): 检索的上下文数量，默认为3
            
        Returns:
            Dict[str, Any]: 包含检索到的上下文和增强提示的结果
        """
        # 如果Milvus连接成功，执行搜索
        if self.milvus_connected:
            try:
                # 生成查询向量
                query_embedding = self.generate_embedding(query)
                
                # 定义搜索参数
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
                
                # 执行搜索
                results = self.milvus_collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=context_size
                )
                
                # 处理搜索结果
                context = []
                for hits in results:
                    for hit in hits:
                        # 查询完整的内容信息
                        content_info = self.milvus_collection.query(
                            expr=f"id == {hit.id}",
                            output_fields=["content", "type", "metadata"]
                        )[0]
                        
                        context.append({
                            "content": content_info["content"],
                            "type": content_info["type"],
                            "similarity": 1.0 / (1.0 + hit.distance)
                        })
                
                # 构建增强提示
                enhanced_prompt = f"Query: {query}\n\nContext:\n"
                for i, item in enumerate(context):
                    enhanced_prompt += f"{i+1}. [{item['type']}] {item['content']}\n"
                
                return {
                    "query": query,
                    "context": context,
                    "enhanced_prompt": enhanced_prompt
                }
            except Exception as e:
                print(f"RAG增强生成失败: {str(e)}")
                # 返回没有上下文的提示
                return {
                    "query": query,
                    "context": [],
                    "enhanced_prompt": f"Query: {query}\n\nContext:\n（无法获取上下文，Milvus连接失败）"
                }
        else:
            print("Milvus未连接，无法进行RAG增强生成")
            # 返回没有上下文的提示
            return {
                "query": query,
                "context": [],
                "enhanced_prompt": f"Query: {query}\n\nContext:\n（无法获取上下文，Milvus未连接）"
            }
    
    def get_test_cases(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取测试用例列表
        
        从MongoDB的test_cases集合中获取测试用例列表，支持过滤条件。
        
        Args:
            filters (Dict[str, Any], optional): 过滤条件，默认为None
            
        Returns:
            List[Dict[str, Any]]: 测试用例列表
        """
        query = filters or {}
        test_cases = list(self.test_cases_collection.find(query))
        # 转换ObjectId为字符串
        for test_case in test_cases:
            test_case["_id"] = str(test_case["_id"])
        return test_cases
    
    def get_defect_patterns(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取缺陷模式列表
        
        从MongoDB的defect_patterns集合中获取缺陷模式列表，支持过滤条件。
        
        Args:
            filters (Dict[str, Any], optional): 过滤条件，默认为None
            
        Returns:
            List[Dict[str, Any]]: 缺陷模式列表
        """
        query = filters or {}
        defect_patterns = list(self.defect_patterns_collection.find(query))
        # 转换ObjectId为字符串
        for defect_pattern in defect_patterns:
            defect_pattern["_id"] = str(defect_pattern["_id"])
        return defect_patterns
    
    def close(self):
        """关闭连接
        
        关闭MongoDB和Milvus的连接。
        """
        self.mongo_client.close()  # 关闭MongoDB连接
        connections.disconnect("default")  # 关闭Milvus连接