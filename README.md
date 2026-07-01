# 出彩中原 - 河南旅游路线导航网站

## 项目简介
河南旅游路线导航网站，展示河南地区精品旅游路线，支持地图可视化展示和路线详情查看。

## 技术栈
### 前端
- Vue3 + Vite
- Element Plus
- Tailwind CSS
- 高德地图 JS API
- Vue Router
- Axios

### 后端
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## 项目结构
```
出彩中原/
├── backend/          # 后端项目
│   ├── app/
│   │   ├── api/      # 路由控制器
│   │   ├── core/     # 核心配置
│   │   ├── db/       # 数据库连接
│   │   ├── models/   # 数据库模型
│   │   ├── schemas/  # 数据校验模型
│   │   └── services/ # 业务逻辑层
│   └── requirements.txt
└── frontend/         # 前端项目（待创建）
```

## 启动方式

### 后端启动
```bash
cd backend
# 使用 uv 管理依赖并启动
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 6567
```

### 前端启动（待前端项目创建后）
```bash
cd frontend
npm install
npm run dev
```

## 开发进度
详见 TODO.md
