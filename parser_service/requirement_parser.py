from typing import List, Dict, Any, Optional
import os
import json
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import (TextLoader, PDFLoader, Docx2txtLoader, 
                                      UnstructuredMarkdownLoader, UnstructuredPDFLoader, 
                                      UnstructuredWordDocumentLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RequirementParser:
    """智能需求解析器
    
    能够从Markdown/Word/PDF中提取结构化需求，使用NLP识别功能点、用户故事、验收标准，
    自动生成测试点清单，识别需求中的歧义和缺失信息，输出JSON格式的测试点图谱。
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """初始化需求解析器
        
        Args:
            api_key (str): OpenAI API密钥
            model (str, optional): 使用的AI模型，默认为"gpt-4"
        """
        self.llm = OpenAI(api_key=api_key, model=model, temperature=0.3)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self._init_prompts()
    
    def _init_prompts(self):
        """初始化提示词模板"""
        # 需求提取提示词
        self.extract_requirements_prompt = PromptTemplate(
            input_variables=["content"],
            template="""
你是一个专业的需求分析师，请从以下内容中提取结构化需求：

{content}

请提取以下信息：
1. 功能点列表
2. 用户故事
3. 验收标准
4. 可能的歧义和缺失信息

请以JSON格式输出，包含以下字段：
- functional_points: 功能点列表
- user_stories: 用户故事列表
- acceptance_criteria: 验收标准列表
- ambiguities: 歧义列表
- missing_info: 缺失信息列表
"""
        )
        
        # 测试点生成提示词
        self.generate_test_points_prompt = PromptTemplate(
            input_variables=["requirements"],
            template="""
你是一个专业的测试工程师，请根据以下需求生成测试点清单：

{requirements}

请为每个功能点生成详细的测试点，包括：
1. 测试用例名称
2. 测试步骤
3. 预期结果
4. 优先级
5. 测试类型

请以JSON格式输出，包含以下字段：
- test_points: 测试点列表
- test_graph: 测试点之间的依赖关系图谱
"""
        )
        
        # 初始化LLM链
        self.extract_chain = LLMChain(llm=self.llm, prompt=self.extract_requirements_prompt)
        self.generate_chain = LLMChain(llm=self.llm, prompt=self.generate_test_points_prompt)
    
    def load_document(self, file_path: str) -> str:
        """加载文档
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            str: 文档内容
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == ".md":
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_extension == ".pdf":
            loader = UnstructuredPDFLoader(file_path)
        elif file_extension in [".docx", ".doc"]:
            loader = UnstructuredWordDocumentLoader(file_path)
        elif file_extension == ".txt":
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
        
        documents = loader.load()
        return "\n".join([doc.page_content for doc in documents])
    
    def parse_requirements(self, content: str) -> Dict[str, Any]:
        """解析需求
        
        Args:
            content (str): 文档内容
            
        Returns:
            Dict[str, Any]: 解析后的需求
        """
        # 分割文本
        chunks = self.text_splitter.split_text(content)
        
        # 处理每个 chunk
        all_requirements = {
            "functional_points": [],
            "user_stories": [],
            "acceptance_criteria": [],
            "ambiguities": [],
            "missing_info": []
        }
        
        for chunk in chunks:
            result = self.extract_chain.run(chunk)
            try:
                chunk_requirements = json.loads(result)
                # 合并结果
                for key in all_requirements:
                    if key in chunk_requirements:
                        all_requirements[key].extend(chunk_requirements[key])
            except json.JSONDecodeError:
                print(f"解析chunk失败: {result}")
        
        # 去重
        for key in all_requirements:
            # 对于字典列表，使用JSON字符串去重
            if isinstance(all_requirements[key], list) and all_requirements[key]:
                seen = set()
                unique_items = []
                for item in all_requirements[key]:
                    item_str = json.dumps(item, sort_keys=True) if isinstance(item, dict) else str(item)
                    if item_str not in seen:
                        seen.add(item_str)
                        unique_items.append(item)
                all_requirements[key] = unique_items
        
        return all_requirements
    
    def generate_test_points(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试点
        
        Args:
            requirements (Dict[str, Any]): 解析后的需求
            
        Returns:
            Dict[str, Any]: 测试点和测试图谱
        """
        requirements_str = json.dumps(requirements, ensure_ascii=False)
        result = self.generate_chain.run(requirements_str)
        
        try:
            test_points_data = json.loads(result)
            return test_points_data
        except json.JSONDecodeError:
            raise ValueError(f"生成测试点失败: {result}")
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """处理文档
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Dict[str, Any]: 包含需求和测试点的完整结果
        """
        # 加载文档
        content = self.load_document(file_path)
        
        # 解析需求
        requirements = self.parse_requirements(content)
        
        # 生成测试点
        test_points_data = self.generate_test_points(requirements)
        
        # 合并结果
        result = {
            "requirements": requirements,
            "test_points": test_points_data.get("test_points", []),
            "test_graph": test_points_data.get("test_graph", {})
        }
        
        return result
    
    def save_result(self, result: Dict[str, Any], output_path: str):
        """保存结果
        
        Args:
            result (Dict[str, Any]): 处理结果
            output_path (str): 输出文件路径
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_path}")

if __name__ == "__main__":
    # 示例用法
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("请设置OPENAI_API_KEY环境变量")
        exit(1)
    
    parser = RequirementParser(api_key=api_key)
    
    # 处理示例文档
    input_file = "example_requirements.md"
    output_file = "parsed_requirements.json"
    
    if os.path.exists(input_file):
        result = parser.process_document(input_file)
        parser.save_result(result, output_file)
        print("文档处理完成！")
    else:
        print(f"文件不存在: {input_file}")