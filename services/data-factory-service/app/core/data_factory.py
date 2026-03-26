import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from faker import Faker
from app.core.database import get_mongo_client
from bson import ObjectId

class DataFactory:
    def __init__(self):
        self.client = get_mongo_client()
        self.db = self.client['data_factory']
        self.schemas_collection = self.db['schemas']
        self.versions_collection = self.db['versions']
        self.faker = Faker()
    
    def create_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建数据模式"""
        schema_data['created_at'] = datetime.now().isoformat()
        schema_data['updated_at'] = datetime.now().isoformat()
        result = self.schemas_collection.insert_one(schema_data)
        schema = self.schemas_collection.find_one({"_id": result.inserted_id})
        schema["_id"] = str(schema["_id"])
        return schema
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """获取所有数据模式"""
        schemas = []
        for schema in self.schemas_collection.find():
            schema["_id"] = str(schema["_id"])
            schemas.append(schema)
        return schemas
    
    def get_schema(self, schema_id: str) -> Dict[str, Any]:
        """根据ID获取数据模式"""
        schema = self.schemas_collection.find_one({"_id": ObjectId(schema_id)})
        if not schema:
            raise Exception("Schema not found")
        schema["_id"] = str(schema["_id"])
        return schema
    
    def generate_data(self, schema_id: str, count: int = 1, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成测试数据"""
        schema = self.get_schema(schema_id)
        
        # 分析依赖关系
        dependencies = self.analyze_dependencies(schema_id)
        
        # 生成数据
        data = []
        for _ in range(count):
            record = self._generate_record(schema, parameters)
            # 脱敏处理
            record = self._mask_sensitive_data(record, schema.get('sensitive_fields', []))
            data.append(record)
        
        # 保存版本
        version_id = self._save_version(schema_id, data)
        
        return {
            "schema_id": schema_id,
            "version_id": version_id,
            "data": data,
            "count": count
        }
    
    def _generate_record(self, schema: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成单条数据记录"""
        record = {}
        fields = schema.get('fields', {})
        
        for field_name, field_config in fields.items():
            field_type = field_config.get('type')
            field_options = field_config.get('options', {})
            
            # 如果提供了参数，优先使用参数值
            if parameters and field_name in parameters:
                record[field_name] = parameters[field_name]
                continue
            
            # 根据字段类型生成数据
            if field_type == 'string':
                record[field_name] = self._generate_string(field_options)
            elif field_type == 'number':
                record[field_name] = self._generate_number(field_options)
            elif field_type == 'boolean':
                record[field_name] = self._generate_boolean(field_options)
            elif field_type == 'date':
                record[field_name] = self._generate_date(field_options)
            elif field_type == 'array':
                record[field_name] = self._generate_array(field_options)
            elif field_type == 'object':
                record[field_name] = self._generate_object(field_options)
            else:
                record[field_name] = None
        
        return record
    
    def _generate_string(self, options: Dict[str, Any]) -> str:
        """生成字符串类型数据"""
        format_type = options.get('format', 'random')
        
        if format_type == 'name':
            return self.faker.name()
        elif format_type == 'email':
            return self.faker.email()
        elif format_type == 'phone':
            return self.faker.phone_number()
        elif format_type == 'address':
            return self.faker.address()
        elif format_type == 'uuid':
            return str(uuid.uuid4())
        elif format_type == 'enum':
            enum_values = options.get('enum', [])
            return self.faker.random_element(enum_values)
        else:
            length = options.get('length', 10)
            return self.faker.pystr(min_chars=length, max_chars=length)
    
    def _generate_number(self, options: Dict[str, Any]) -> float:
        """生成数字类型数据"""
        min_value = options.get('min', 0)
        max_value = options.get('max', 100)
        decimal_places = options.get('decimal_places', 0)
        
        if decimal_places > 0:
            return round(self.faker.uniform(min_value, max_value), decimal_places)
        else:
            return self.faker.random_int(min=min_value, max=max_value)
    
    def _generate_boolean(self, options: Dict[str, Any]) -> bool:
        """生成布尔类型数据"""
        probability = options.get('probability', 0.5)
        return self.faker.boolean(chance_of_getting_true=probability * 100)
    
    def _generate_date(self, options: Dict[str, Any]) -> str:
        """生成日期类型数据"""
        start_date = options.get('start_date', '-30d')
        end_date = options.get('end_date', 'today')
        format = options.get('format', '%Y-%m-%d')
        
        return self.faker.date_between(start_date=start_date, end_date=end_date).strftime(format)
    
    def _generate_array(self, options: Dict[str, Any]) -> List[Any]:
        """生成数组类型数据"""
        item_type = options.get('item_type', 'string')
        min_items = options.get('min_items', 1)
        max_items = options.get('max_items', 5)
        
        items = []
        item_count = self.faker.random_int(min=min_items, max=max_items)
        
        for _ in range(item_count):
            if item_type == 'string':
                items.append(self._generate_string({}))
            elif item_type == 'number':
                items.append(self._generate_number({}))
            elif item_type == 'boolean':
                items.append(self._generate_boolean({}))
        
        return items
    
    def _generate_object(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """生成对象类型数据"""
        properties = options.get('properties', {})
        obj = {}
        
        for prop_name, prop_config in properties.items():
            prop_type = prop_config.get('type')
            prop_options = prop_config.get('options', {})
            
            if prop_type == 'string':
                obj[prop_name] = self._generate_string(prop_options)
            elif prop_type == 'number':
                obj[prop_name] = self._generate_number(prop_options)
            elif prop_type == 'boolean':
                obj[prop_name] = self._generate_boolean(prop_options)
        
        return obj
    
    def _mask_sensitive_data(self, record: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """脱敏处理敏感数据"""
        for field in sensitive_fields:
            if field in record:
                if isinstance(record[field], str):
                    if '@' in record[field]:  # 邮箱
                        username, domain = record[field].split('@')
                        record[field] = f"{username[:3]}***@{domain}"
                    elif record[field].isdigit() and len(record[field]) >= 8:  # 电话号码或身份证
                        record[field] = f"{record[field][:3]}***{record[field][-3:]}"
                    else:
                        record[field] = "***"
        return record
    
    def _save_version(self, schema_id: str, data: List[Dict[str, Any]]) -> str:
        """保存数据版本"""
        version_data = {
            "schema_id": schema_id,
            "data": data,
            "created_at": datetime.now().isoformat(),
            "version": self._get_next_version(schema_id)
        }
        
        result = self.versions_collection.insert_one(version_data)
        return str(result.inserted_id)
    
    def _get_next_version(self, schema_id: str) -> int:
        """获取下一个版本号"""
        last_version = self.versions_collection.find_one(
            {"schema_id": schema_id},
            sort=[("version", -1)]
        )
        if last_version:
            return last_version.get("version", 0) + 1
        return 1
    
    def get_versions(self, schema_id: str) -> List[Dict[str, Any]]:
        """获取数据版本历史"""
        versions = []
        for version in self.versions_collection.find({"schema_id": schema_id}).sort("version", -1):
            version["_id"] = str(version["_id"])
            versions.append(version)
        return versions
    
    def rollback_version(self, schema_id: str, version_id: str) -> Dict[str, str]:
        """回滚数据版本"""
        version = self.versions_collection.find_one({"_id": ObjectId(version_id), "schema_id": schema_id})
        if not version:
            raise Exception("Version not found")
        
        # 这里可以实现具体的回滚逻辑，例如将当前数据替换为版本数据
        # 为了演示，我们只是返回成功消息
        return {"message": f"Rolled back to version {version.get('version')}"}
    
    def analyze_dependencies(self, schema_id: str) -> Dict[str, Any]:
        """分析数据依赖关系"""
        schema = self.get_schema(schema_id)
        fields = schema.get('fields', {})
        
        dependencies = {
            "schema_id": schema_id,
            "dependencies": [],
            "field_relations": []
        }
        
        # 分析字段间的依赖关系
        for field_name, field_config in fields.items():
            if 'depends_on' in field_config:
                dependencies['dependencies'].append({
                    "field": field_name,
                    "depends_on": field_config['depends_on']
                })
            
            # 分析字段间的关系
            if field_config.get('type') == 'object' and 'properties' in field_config.get('options', {}):
                nested_fields = field_config['options']['properties']
                for nested_field in nested_fields:
                    dependencies['field_relations'].append({
                        "parent": field_name,
                        "child": nested_field
                    })
        
        return dependencies