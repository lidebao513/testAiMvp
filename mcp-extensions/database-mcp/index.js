const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const mysql = require('mysql2/promise');
const { Client } = require('pg');
const mongoose = require('mongoose');
const faker = require('faker');
const app = express();
const port = 3008;

app.use(bodyParser.json());

// 配置信息
const config = {
  databases: {
    mysql: {
      host: 'localhost',
      port: 3306,
      user: 'root',
      password: 'test123',
      database: 'test_db'
    },
    postgres: {
      host: 'localhost',
      port: 5432,
      user: 'postgres',
      password: 'test123',
      database: 'test_db'
    },
    mongodb: {
      uri: 'mongodb://localhost:27017/test_db'
    }
  }
};

// MySQL连接
const getMysqlConnection = async () => {
  return await mysql.createConnection(config.databases.mysql);
};

// PostgreSQL连接
const getPostgresConnection = async () => {
  const client = new Client(config.databases.postgres);
  await client.connect();
  return client;
};

// MongoDB连接
const getMongoConnection = async () => {
  if (!mongoose.connection.readyState) {
    await mongoose.connect(config.databases.mongodb.uri);
  }
  return mongoose.connection;
};

// 生成测试数据
const generateTestData = (type, count = 10) => {
  const data = [];
  
  for (let i = 0; i < count; i++) {
    switch (type) {
      case 'user':
        data.push({
          id: i + 1,
          name: faker.name.findName(),
          email: faker.internet.email(),
          password: faker.internet.password(),
          createdAt: new Date(),
          updatedAt: new Date()
        });
        break;
      case 'product':
        data.push({
          id: i + 1,
          name: faker.commerce.productName(),
          description: faker.commerce.productDescription(),
          price: parseFloat(faker.commerce.price()),
          stock: faker.random.number(100),
          createdAt: new Date(),
          updatedAt: new Date()
        });
        break;
      case 'order':
        data.push({
          id: i + 1,
          userId: faker.random.number(10),
          totalAmount: parseFloat(faker.commerce.price()),
          status: faker.random.arrayElement(['pending', 'completed', 'cancelled']),
          createdAt: new Date(),
          updatedAt: new Date()
        });
        break;
      default:
        data.push({
          id: i + 1,
          name: faker.lorem.word(),
          value: faker.lorem.sentence(),
          createdAt: new Date()
        });
    }
  }
  
  return data;
};

// 初始化MySQL表结构
const initMysqlTables = async () => {
  const connection = await getMysqlConnection();
  
  try {
    // 创建用户表
    await connection.execute(`
      CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);
    
    // 创建产品表
    await connection.execute(`
      CREATE TABLE IF NOT EXISTS products (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        stock INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
      )
    `);
    
    // 创建订单表
    await connection.execute(`
      CREATE TABLE IF NOT EXISTS orders (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT,
        total_amount DECIMAL(10, 2) NOT NULL,
        status VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
      )
    `);
    
    console.log('MySQL表结构初始化完成');
  } catch (error) {
    console.error('初始化MySQL表结构失败:', error);
  } finally {
    await connection.end();
  }
};

// 初始化PostgreSQL表结构
const initPostgresTables = async () => {
  const client = await getPostgresConnection();
  
  try {
    // 创建用户表
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // 创建产品表
    await client.query(`
      CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        stock INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // 创建订单表
    await client.query(`
      CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INT,
        total_amount DECIMAL(10, 2) NOT NULL,
        status VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
      )
    `);
    
    console.log('PostgreSQL表结构初始化完成');
  } catch (error) {
    console.error('初始化PostgreSQL表结构失败:', error);
  } finally {
    await client.end();
  }
};

// 初始化MongoDB集合
const initMongoCollections = async () => {
  const connection = await getMongoConnection();
  
  try {
    // 检查并创建集合
    const collections = ['users', 'products', 'orders'];
    for (const collection of collections) {
      if (!connection.collection(collection)) {
        await connection.createCollection(collection);
        console.log(`MongoDB集合 ${collection} 创建完成`);
      }
    }
    
    console.log('MongoDB集合初始化完成');
  } catch (error) {
    console.error('初始化MongoDB集合失败:', error);
  }
};

// 向MySQL插入测试数据
const insertMysqlTestData = async (table, data) => {
  const connection = await getMysqlConnection();
  
  try {
    if (data.length === 0) return;
    
    const keys = Object.keys(data[0]);
    const values = data.map(item => keys.map(key => item[key]));
    
    const placeholders = values.map(() => `(${keys.map(() => '?').join(', ')})`).join(', ');
    const query = `INSERT INTO ${table} (${keys.join(', ')}) VALUES ${placeholders}`;
    
    await connection.execute(query, values.flat());
    console.log(`向MySQL表 ${table} 插入 ${data.length} 条测试数据`);
  } catch (error) {
    console.error(`向MySQL表 ${table} 插入测试数据失败:`, error);
  } finally {
    await connection.end();
  }
};

// 向PostgreSQL插入测试数据
const insertPostgresTestData = async (table, data) => {
  const client = await getPostgresConnection();
  
  try {
    if (data.length === 0) return;
    
    const keys = Object.keys(data[0]);
    const values = data.map(item => keys.map(key => item[key]));
    
    const placeholders = values.map((_, idx) => `(${keys.map((_, kdx) => `$${idx * keys.length + kdx + 1}`).join(', ')})`).join(', ');
    const query = `INSERT INTO ${table} (${keys.join(', ')}) VALUES ${placeholders}`;
    
    await client.query(query, values.flat());
    console.log(`向PostgreSQL表 ${table} 插入 ${data.length} 条测试数据`);
  } catch (error) {
    console.error(`向PostgreSQL表 ${table} 插入测试数据失败:`, error);
  } finally {
    await client.end();
  }
};

// 向MongoDB插入测试数据
const insertMongoTestData = async (collection, data) => {
  const connection = await getMongoConnection();
  
  try {
    if (data.length === 0) return;
    
    await connection.collection(collection).insertMany(data);
    console.log(`向MongoDB集合 ${collection} 插入 ${data.length} 条测试数据`);
  } catch (error) {
    console.error(`向MongoDB集合 ${collection} 插入测试数据失败:`, error);
  }
};

// 初始化数据库
app.post('/init/:database', async (req, res) => {
  const database = req.params.database;
  
  try {
    switch (database) {
      case 'mysql':
        await initMysqlTables();
        break;
      case 'postgres':
        await initPostgresTables();
        break;
      case 'mongodb':
        await initMongoCollections();
        break;
      default:
        return res.status(400).send({ message: '不支持的数据库类型' });
    }
    
    res.status(200).send({ message: `${database} 数据库初始化完成` });
  } catch (error) {
    console.error(`初始化 ${database} 数据库失败:`, error);
    res.status(500).send({ message: `初始化 ${database} 数据库失败`, error: error.message });
  }
});

// 生成测试数据
app.post('/generate/:database', async (req, res) => {
  const database = req.params.database;
  const { table, type, count = 10 } = req.body;
  
  if (!table || !type) {
    return res.status(400).send({ message: '缺少必要参数: table 和 type' });
  }
  
  try {
    const testData = generateTestData(type, count);
    
    switch (database) {
      case 'mysql':
        await insertMysqlTestData(table, testData);
        break;
      case 'postgres':
        await insertPostgresTestData(table, testData);
        break;
      case 'mongodb':
        await insertMongoTestData(table, testData);
        break;
      default:
        return res.status(400).send({ message: '不支持的数据库类型' });
    }
    
    res.status(200).send({ message: `向 ${database} 的 ${table} 生成 ${count} 条测试数据`, data: testData });
  } catch (error) {
    console.error(`生成测试数据失败:`, error);
    res.status(500).send({ message: '生成测试数据失败', error: error.message });
  }
});

// 清空数据库
app.post('/clear/:database', async (req, res) => {
  const database = req.params.database;
  const { table } = req.body;
  
  if (!table) {
    return res.status(400).send({ message: '缺少必要参数: table' });
  }
  
  try {
    switch (database) {
      case 'mysql':
        const mysqlConnection = await getMysqlConnection();
        await mysqlConnection.execute(`TRUNCATE TABLE ${table}`);
        await mysqlConnection.end();
        break;
      case 'postgres':
        const postgresClient = await getPostgresConnection();
        await postgresClient.query(`TRUNCATE TABLE ${table} CASCADE`);
        await postgresClient.end();
        break;
      case 'mongodb':
        const mongoConnection = await getMongoConnection();
        await mongoConnection.collection(table).deleteMany({});
        break;
      default:
        return res.status(400).send({ message: '不支持的数据库类型' });
    }
    
    res.status(200).send({ message: `清空 ${database} 的 ${table} 数据完成` });
  } catch (error) {
    console.error(`清空数据库失败:`, error);
    res.status(500).send({ message: '清空数据库失败', error: error.message });
  }
});

// 获取数据库状态
app.get('/status/:database', async (req, res) => {
  const database = req.params.database;
  
  try {
    let status = {};
    
    switch (database) {
      case 'mysql':
        const mysqlConnection = await getMysqlConnection();
        const mysqlTables = await mysqlConnection.execute('SHOW TABLES');
        status.tables = mysqlTables[0].map(row => Object.values(row)[0]);
        await mysqlConnection.end();
        break;
      case 'postgres':
        const postgresClient = await getPostgresConnection();
        const postgresTables = await postgresClient.query('\dt');
        status.tables = postgresTables.rows.map(row => row.tablename);
        await postgresClient.end();
        break;
      case 'mongodb':
        const mongoConnection = await getMongoConnection();
        const mongoCollections = await mongoConnection.listCollections().toArray();
        status.collections = mongoCollections.map(col => col.name);
        break;
      default:
        return res.status(400).send({ message: '不支持的数据库类型' });
    }
    
    res.status(200).send({ message: `${database} 数据库状态`, status });
  } catch (error) {
    console.error(`获取数据库状态失败:`, error);
    res.status(500).send({ message: '获取数据库状态失败', error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Database MCP 服务运行在 http://localhost:${port}`);
  console.log('初始化数据库地址: http://localhost:${port}/init/:database');
  console.log('生成测试数据地址: http://localhost:${port}/generate/:database');
  console.log('清空数据库地址: http://localhost:${port}/clear/:database');
  console.log('获取数据库状态地址: http://localhost:${port}/status/:database');
});

module.exports = app;