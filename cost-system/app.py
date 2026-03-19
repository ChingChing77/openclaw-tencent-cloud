import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_NAME = "cost_system.db"

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 成本预算表
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        cost_type TEXT,
        budget_amount REAL,
        actual_amount REAL,
        difference REAL,
        status TEXT DEFAULT '进行中',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 项目进度表
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        responsible_person TEXT,
        start_date TEXT,
        end_date TEXT,
        progress_percent INTEGER DEFAULT 0,
        status TEXT DEFAULT '进行中',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 合同管理表
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_name TEXT NOT NULL,
        contract_amount REAL,
        sign_date TEXT,
        contract_status TEXT DEFAULT '执行中',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 费用报销表
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_type TEXT NOT NULL,
        amount REAL,
        expense_date TEXT,
        approval_status TEXT DEFAULT '待审批',
        remark TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 操作日志表
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        detail TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 插入示例数据
    c.execute("SELECT COUNT(*) FROM budgets")
    if c.fetchone()[0] == 0:
        sample_budgets = [
            ('土建工程', '人工费', 500000, 550000, 50000),
            ('设备采购', '设备费', 300000, 280000, -20000),
            ('安装工程', '材料费', 200000, 220000, 20000),
            ('装修工程', '装饰费', 150000, 160000, 10000),
        ]
        c.executemany("INSERT INTO budgets (project_name, cost_type, budget_amount, actual_amount, difference) VALUES (?, ?, ?, ?, ?)", sample_budgets)
        
        sample_progress = [
            ('项目A', '张三', '2024-01-01', '2024-12-31', 50),
            ('项目B', '李四', '2024-03-01', '2024-10-31', 30),
        ]
        c.executemany("INSERT INTO progress (project_name, responsible_person, start_date, end_date, progress_percent) VALUES (?, ?, ?, ?, ?)", sample_progress)
        
        sample_contracts = [
            ('采购合同A', 200000, '2024-01-15', '执行中'),
            ('施工合同B', 500000, '2024-02-01', '执行中'),
        ]
        c.executemany("INSERT INTO contracts (contract_name, contract_amount, sign_date, contract_status) VALUES (?, ?, ?, ?)", sample_contracts)
        
        sample_expenses = [
            ('差旅费', 2000, '2024-01-15', '已审批', '北京出差'),
            ('餐饮费', 1500, '2024-01-20', '待审批', '客户接待'),
        ]
        c.executemany("INSERT INTO expenses (expense_type, amount, expense_date, approval_status, remark) VALUES (?, ?, ?, ?, ?)", sample_expenses)
        
        conn.commit()
        print("✅ 示例数据已插入")
    
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def add_log(action, detail):
    conn = get_db_connection()
    conn.execute("INSERT INTO logs (action, detail) VALUES (?, ?)", (action, detail))
    conn.commit()
    conn.close()

# ==================== 路由 ====================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# 首页统计数据
@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    
    budgets = conn.execute("SELECT COUNT(*) as count, SUM(budget_amount) as total_budget, SUM(actual_amount) as total_actual FROM budgets").fetchone()
    progress = conn.execute("SELECT COUNT(*) as count FROM progress").fetchone()
    contracts = conn.execute("SELECT COUNT(*) as count, SUM(contract_amount) as total FROM contracts").fetchone()
    expenses = conn.execute("SELECT COUNT(*) as count, SUM(amount) as total FROM expenses").fetchone()
    
    conn.close()
    
    return jsonify({
        'budget_count': budgets['count'] or 0,
        'total_budget': budgets['total_budget'] or 0,
        'total_actual': budgets['total_actual'] or 0,
        'progress_count': progress['count'] or 0,
        'contract_count': contracts['count'] or 0,
        'contract_total': contracts['total'] or 0,
        'expense_count': expenses['count'] or 0,
        'expense_total': expenses['total'] or 0,
    })

# ==================== 成本预算管理 ====================

@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    conn = get_db_connection()
    budgets = conn.execute("SELECT * FROM budgets ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in budgets])

@app.route('/api/budgets', methods=['POST'])
def add_budget():
    data = request.json
    conn = get_db_connection()
    conn.execute("""INSERT INTO budgets (project_name, cost_type, budget_amount, actual_amount, difference, status) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (data['project_name'], data.get('cost_type'), data.get('budget_amount'), 
                 data.get('actual_amount'), data.get('difference'), data.get('status', '进行中')))
    conn.commit()
    conn.close()
    add_log('添加预算', f"项目: {data['project_name']}")
    return jsonify({'success': True})

@app.route('/api/budgets/<int:id>', methods=['PUT'])
def update_budget(id):
    data = request.json
    conn = get_db_connection()
    conn.execute("""UPDATE budgets SET project_name=?, cost_type=?, budget_amount=?, actual_amount=?, difference=?, status=? WHERE id=?""",
                (data['project_name'], data['cost_type'], data['budget_amount'], 
                 data['actual_amount'], data['difference'], data['status'], id))
    conn.commit()
    conn.close()
    add_log('更新预算', f"ID: {id}")
    return jsonify({'success': True})

@app.route('/api/budgets/<int:id>', methods=['DELETE'])
def delete_budget(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM budgets WHERE id=?", (id,))
    conn.commit()
    conn.close()
    add_log('删除预算', f"ID: {id}")
    return jsonify({'success': True})

# ==================== 项目进度追踪 ====================

@app.route('/api/progress', methods=['GET'])
def get_progress():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM progress ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in items])

@app.route('/api/progress', methods=['POST'])
def add_progress():
    data = request.json
    conn = get_db_connection()
    conn.execute("""INSERT INTO progress (project_name, responsible_person, start_date, end_date, progress_percent, status) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (data['project_name'], data.get('responsible_person'), data.get('start_date'),
                 data.get('end_date'), data.get('progress_percent', 0), data.get('status', '进行中')))
    conn.commit()
    conn.close()
    add_log('添加进度', f"项目: {data['project_name']}")
    return jsonify({'success': True})

@app.route('/api/progress/<int:id>', methods=['PUT'])
def update_progress(id):
    data = request.json
    conn = get_db_connection()
    conn.execute("""UPDATE progress SET project_name=?, responsible_person=?, start_date=?, end_date=?, progress_percent=?, status=? WHERE id=?""",
                (data['project_name'], data['responsible_person'], data['start_date'],
                 data['end_date'], data['progress_percent'], data['status'], id))
    conn.commit()
    conn.close()
    add_log('更新进度', f"ID: {id}")
    return jsonify({'success': True})

@app.route('/api/progress/<int:id>', methods=['DELETE'])
def delete_progress(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM progress WHERE id=?", (id,))
    conn.commit()
    conn.close()
    add_log('删除进度', f"ID: {id}")
    return jsonify({'success': True})

# ==================== 合同管理 ====================

@app.route('/api/contracts', methods=['GET'])
def get_contracts():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM contracts ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in items])

@app.route('/api/contracts', methods=['POST'])
def add_contract():
    data = request.json
    conn = get_db_connection()
    conn.execute("""INSERT INTO contracts (contract_name, contract_amount, sign_date, contract_status) 
                   VALUES (?, ?, ?, ?)""",
                (data['contract_name'], data.get('contract_amount'), data.get('sign_date'), 
                 data.get('contract_status', '执行中')))
    conn.commit()
    conn.close()
    add_log('添加合同', f"合同: {data['contract_name']}")
    return jsonify({'success': True})

@app.route('/api/contracts/<int:id>', methods=['PUT'])
def update_contract(id):
    data = request.json
    conn = get_db_connection()
    conn.execute("""UPDATE contracts SET contract_name=?, contract_amount=?, sign_date=?, contract_status=? WHERE id=?""",
                (data['contract_name'], data['contract_amount'], data['sign_date'], data['contract_status'], id))
    conn.commit()
    conn.close()
    add_log('更新合同', f"ID: {id}")
    return jsonify({'success': True})

@app.route('/api/contracts/<int:id>', methods=['DELETE'])
def delete_contract(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM contracts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    add_log('删除合同', f"ID: {id}")
    return jsonify({'success': True})

# ==================== 费用报销 ====================

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM expenses ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in items])

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    conn = get_db_connection()
    conn.execute("""INSERT INTO expenses (expense_type, amount, expense_date, approval_status, remark) 
                   VALUES (?, ?, ?, ?, ?)""",
                (data['expense_type'], data.get('amount'), data.get('expense_date'),
                 data.get('approval_status', '待审批'), data.get('remark')))
    conn.commit()
    conn.close()
    add_log('添加报销', f"类型: {data['expense_type']}, 金额: {data.get('amount')}")
    return jsonify({'success': True})

@app.route('/api/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    data = request.json
    conn = get_db_connection()
    conn.execute("""UPDATE expenses SET expense_type=?, amount=?, expense_date=?, approval_status=?, remark=? WHERE id=?""",
                (data['expense_type'], data['amount'], data['expense_date'], 
                 data['approval_status'], data['remark'], id))
    conn.commit()
    conn.close()
    add_log('更新报销', f"ID: {id}")
    return jsonify({'success': True})

@app.route('/api/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    add_log('删除报销', f"ID: {id}")
    return jsonify({'success': True})

# ==================== 日志 ====================

@app.route('/api/logs', methods=['GET'])
def get_logs():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return jsonify([dict(row) for row in items])

# ==================== 前端页面 ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工程造价成本建档系统</title>
    <link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css">
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://unpkg.com/element-plus"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header .subtitle { opacity: 0.9; font-size: 14px; }
        .main-container { display: flex; min-height: calc(100vh - 80px); }
        .sidebar { width: 200px; background: white; box-shadow: 2px 0 8px rgba(0,0,0,0.05); }
        .sidebar-menu { list-style: none; }
        .sidebar-menu li { padding: 15px 20px; cursor: pointer; border-left: 3px solid transparent; transition: all 0.3s; }
        .sidebar-menu li:hover { background: #f5f7fa; }
        .sidebar-menu li.active { background: #f0f5ff; border-left-color: #667eea; color: #667eea; font-weight: 600; }
        .content { flex: 1; padding: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
        .stat-card h3 { font-size: 14px; color: #909399; margin-bottom: 10px; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: #303133; }
        .stat-card .value.green { color: #67c23a; }
        .stat-card .value.orange { color: #e6a23c; }
        .page-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; color: #303133; }
        .toolbar { display: flex; gap: 10px; margin-bottom: 20px; }
        .data-table { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <div>
                <h1>🏗️ 工程造价成本建档系统</h1>
                <div class="subtitle">V1.0 精简版</div>
            </div>
            <div>{{ currentTime }}</div>
        </div>
        
        <div class="main-container">
            <ul class="sidebar-menu">
                <li :class="{active: currentPage === 'home'}" @click="currentPage = 'home'">📊 首页</li>
                <li :class="{active: currentPage === 'budget'}" @click="currentPage = 'budget'">💰 成本预算管理</li>
                <li :class="{active: currentPage === 'progress'}" @click="currentPage = 'progress'">📈 项目进度追踪</li>
                <li :class="{active: currentPage === 'contract'}" @click="currentPage = 'contract'">📄 合同管理</li>
                <li :class="{active: currentPage === 'expense'}" @click="currentPage = 'expense'">💳 费用报销记录</li>
                <li :class="{active: currentPage === 'log'}" @click="currentPage = 'log'">📝 日志消息</li>
            </ul>
            
            <div class="content">
                <!-- 首页 -->
                <div v-if="currentPage === 'home'">
                    <div class="page-title">📊 数据概览</div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h3>预算项目数</h3>
                            <div class="value">{{ stats.budget_count }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>总预算金额</h3>
                            <div class="value">¥{{ formatNumber(stats.total_budget) }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>实际支出</h3>
                            <div class="value orange">¥{{ formatNumber(stats.total_actual) }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>进行中项目</h3>
                            <div class="value green">{{ stats.progress_count }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>合同数量</h3>
                            <div class="value">{{ stats.contract_count }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>合同总金额</h3>
                            <div class="value">¥{{ formatNumber(stats.contract_total) }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>报销记录</h3>
                            <div class="value">{{ stats.expense_count }}</div>
                        </div>
                        <div class="stat-card">
                            <h3>报销总额</h3>
                            <div class="value orange">¥{{ formatNumber(stats.expense_total) }}</div>
                        </div>
                    </div>
                </div>
                
                <!-- 成本预算管理 -->
                <div v-if="currentPage === 'budget'">
                    <div class="page-title">💰 成本预算管理</div>
                    <div class="toolbar">
                        <el-button type="primary" @click="showAddDialog('budget')">➕ 添加</el-button>
                    </div>
                    <div class="data-table">
                        <el-table :data="budgets" stripe>
                            <el-table-column prop="id" label="ID" width="60"></el-table-column>
                            <el-table-column prop="project_name" label="项目名称"></el-table-column>
                            <el-table-column prop="cost_type" label="费用类型"></el-table-column>
                            <el-table-column prop="budget_amount" label="预算金额">
                                <template #default="scope">¥{{ formatNumber(scope.row.budget_amount) }}</template>
                            </el-table-column>
                            <el-table-column prop="actual_amount" label="实际金额">
                                <template #default="scope">¥{{ formatNumber(scope.row.actual_amount) }}</template>
                            </el-table-column>
                            <el-table-column prop="difference" label="差异">
                                <template #default="scope">
                                    <span :style="{color: scope.row.difference > 0 ? '#f56c6c' : '#67c23a'}">
                                        {{ scope.row.difference > 0 ? '+' : '' }}{{ formatNumber(scope.row.difference) }}
                                    </span>
                                </template>
                            </el-table-column>
                            <el-table-column prop="status" label="状态" width="100">
                                <template #default="scope">
                                    <el-tag :type="scope.row.status === '已完成' ? 'success' : 'primary'">{{ scope.row.status }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" width="150">
                                <template #default="scope">
                                    <el-button size="small" @click="editItem('budget', scope.row)">编辑</el-button>
                                    <el-button size="small" type="danger" @click="deleteItem('budget', scope.row.id)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
                
                <!-- 项目进度追踪 -->
                <div v-if="currentPage === 'progress'">
                    <div class="page-title">📈 项目进度追踪</div>
                    <div class="toolbar">
                        <el-button type="primary" @click="showAddDialog('progress')">➕ 新增数据</el-button>
                    </div>
                    <div class="data-table">
                        <el-table :data="progress" stripe>
                            <el-table-column prop="id" label="ID" width="60"></el-table-column>
                            <el-table-column prop="project_name" label="项目名称"></el-table-column>
                            <el-table-column prop="responsible_person" label="负责人"></el-table-column>
                            <el-table-column prop="start_date" label="开始日期"></el-table-column>
                            <el-table-column prop="end_date" label="结束日期"></el-table-column>
                            <el-table-column prop="progress_percent" label="进度%" width="100">
                                <template #default="scope">
                                    <el-progress :percentage="scope.row.progress_percent" :status="scope.row.progress_percent === 100 ? 'success' : ''"></el-progress>
                                </template>
                            </el-table-column>
                            <el-table-column prop="status" label="状态" width="100">
                                <template #default="scope">
                                    <el-tag :type="scope.row.status === '已完成' ? 'success' : 'primary'">{{ scope.row.status }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" width="150">
                                <template #default="scope">
                                    <el-button size="small" @click="editItem('progress', scope.row)">编辑</el-button>
                                    <el-button size="small" type="danger" @click="deleteItem('progress', scope.row.id)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
                
                <!-- 合同管理 -->
                <div v-if="currentPage === 'contract'">
                    <div class="page-title">📄 合同管理</div>
                    <div class="toolbar">
                        <el-button type="primary" @click="showAddDialog('contract')">➕ 添加</el-button>
                    </div>
                    <div class="data-table">
                        <el-table :data="contracts" stripe>
                            <el-table-column prop="id" label="ID" width="60"></el-table-column>
                            <el-table-column prop="contract_name" label="合同名称"></el-table-column>
                            <el-table-column prop="contract_amount" label="合同金额">
                                <template #default="scope">¥{{ formatNumber(scope.row.contract_amount) }}</template>
                            </el-table-column>
                            <el-table-column prop="sign_date" label="签订日期"></el-table-column>
                            <el-table-column prop="contract_status" label="状态" width="100">
                                <template #default="scope">
                                    <el-tag :type="scope.row.contract_status === '执行中' ? 'success' : 'info'">{{ scope.row.contract_status }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作" width="150">
                                <template #default="scope">
                                    <el-button size="small" @click="editItem('contract', scope.row)">编辑</el-button>
                                    <el-button size="small" type="danger" @click="deleteItem('contract', scope.row.id)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
                
                <!-- 费用报销 -->
                <div v-if="currentPage === 'expense'">
                    <div class="page-title">💳 费用报销记录</div>
                    <div class="toolbar">
                        <el-button type="primary" @click="showAddDialog('expense')">➕ 添加</el-button>
                    </div>
                    <div class="data-table">
                        <el-table :data="expenses" stripe>
                            <el-table-column prop="id" label="ID" width="60"></el-table-column>
                            <el-table-column prop="expense_type" label="费用类型"></el-table-column>
                            <el-table-column prop="amount" label="金额">
                                <template #default="scope">¥{{ formatNumber(scope.row.amount) }}</template>
                            </el-table-column>
                            <el-table-column prop="expense_date" label="报销日期"></el-table-column>
                            <el-table-column prop="approval_status" label="审批状态" width="100">
                                <template #default="scope">
                                    <el-tag :type="scope.row.approval_status === '已审批' ? 'success' : 'warning'">{{ scope.row.approval_status }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="remark" label="备注"></el-table-column>
                            <el-table-column label="操作" width="150">
                                <template #default="scope">
                                    <el-button size="small" @click="editItem('expense', scope.row)">编辑</el-button>
                                    <el-button size="small" type="danger" @click="deleteItem('expense', scope.row.id)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
                
                <!-- 日志 -->
                <div v-if="currentPage === 'log'">
                    <div class="page-title">📝 操作日志</div>
                    <div class="data-table">
                        <el-table :data="logs" stripe>
                            <el-table-column prop="id" label="ID" width="60"></el-table-column>
                            <el-table-column prop="action" label="操作"></el-table-column>
                            <el-table-column prop="detail" label="详情"></el-table-column>
                            <el-table-column prop="created_at" label="时间"></el-table-column>
                        </el-table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 添加/编辑对话框 -->
        <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
            <el-form :model="formData" label-width="100px">
                <el-form-item v-for="(value, key) in formFields" :key="key" :label="value.label">
                    <el-input v-if="value.type === 'text'" v-model="formData[key]"></el-input>
                    <el-input-number v-else-if="value.type === 'number'" v-model="formData[key]" :step="value.step || 1"></el-input-number>
                    <el-select v-else-if="value.type === 'select'" v-model="formData[key]">
                        <el-option v-for="opt in value.options" :key="opt" :label="opt" :value="opt"></el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="submitForm">确认</el-button>
            </template>
        </el-dialog>
    </div>
    
    <script>
        const { createApp, ref, onMounted, computed } = Vue;
        
        const app = createApp({
            setup() {
                const currentPage = ref('home');
                const currentTime = ref('');
                const stats = ref({});
                const budgets = ref([]);
                const progress = ref([]);
                const contracts = ref([]);
                const expenses = ref([]);
                const logs = ref([]);
                
                const dialogVisible = ref(false);
                const dialogType = ref('');
                const editId = ref(null);
                const formData = ref({});
                
                const formFields = {
                    budget: {
                        project_name: { label: '项目名称', type: 'text' },
                        cost_type: { label: '费用类型', type: 'text' },
                        budget_amount: { label: '预算金额', type: 'number' },
                        actual_amount: { label: '实际金额', type: 'number' },
                        difference: { label: '差异', type: 'number' },
                        status: { label: '状态', type: 'select', options: ['进行中', '已完成'] }
                    },
                    progress: {
                        project_name: { label: '项目名称', type: 'text' },
                        responsible_person: { label: '负责人', type: 'text' },
                        start_date: { label: '开始日期', type: 'text' },
                        end_date: { label: '结束日期', type: 'text' },
                        progress_percent: { label: '进度%', type: 'number', step: 5 },
                        status: { label: '状态', type: 'select', options: ['进行中', '已完成'] }
                    },
                    contract: {
                        contract_name: { label: '合同名称', type: 'text' },
                        contract_amount: { label: '合同金额', type: 'number' },
                        sign_date: { label: '签订日期', type: 'text' },
                        contract_status: { label: '状态', type: 'select', options: ['执行中', '已完成', '已终止'] }
                    },
                    expense: {
                        expense_type: { label: '费用类型', type: 'text' },
                        amount: { label: '金额', type: 'number' },
                        expense_date: { label: '报销日期', type: 'text' },
                        approval_status: { label: '审批状态', type: 'select', options: ['待审批', '已审批', '已拒绝'] },
                        remark: { label: '备注', type: 'text' }
                    }
                };
                
                const dialogTitle = computed(() => {
                    if (editId.value) return '编辑' + {budget: '预算', progress: '进度', contract: '合同', expense: '报销'}[dialogType.value];
                    return '添加' + {budget: '预算', progress: '进度', contract: '合同', expense: '报销'}[dialogType.value];
                });
                
                const updateTime = () => {
                    const now = new Date();
                    currentTime.value = now.toLocaleString('zh-CN');
                };
                
                const formatNumber = (num) => {
                    if (!num) return '0';
                    return Number(num).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                };
                
                const loadStats = async () => {
                    const res = await axios.get('/api/stats');
                    stats.value = res.data;
                };
                
                const loadData = async (type) => {
                    const res = await axios.get('/api/' + type);
                    if (type === 'budget') budgets.value = res.data;
                    if (type === 'progress') progress.value = res.data;
                    if (type === 'contract') contracts.value = res.data;
                    if (type === 'expense') expenses.value = res.data;
                    if (type === 'log') logs.value = res.data;
                };
                
                const showAddDialog = (type) => {
                    dialogType.value = type;
                    editId.value = null;
                    formData.value = {};
                    Object.keys(formFields[type]).forEach(key => {
                        formData.value[key] = type === 'progress' && key === 'progress_percent' ? 0 : '';
                    });
                    dialogVisible.value = true;
                };
                
                const editItem = (type, row) => {
                    dialogType.value = type;
                    editId.value = row.id;
                    formData.value = {...row};
                    dialogVisible.value = true;
                };
                
                const deleteItem = async (type, id) => {
                    await ElMessageBox.confirm('确认删除?', '提示', {type: 'warning'});
                    await axios.delete('/api/' + type + '/' + id);
                    ElMessage.success('删除成功');
                    loadData(type);
                    loadStats();
                };
                
                const submitForm = async () => {
                    if (editId.value) {
                        await axios.put('/api/' + dialogType.value + '/' + editId.value, formData.value);
                    } else {
                        await axios.post('/api/' + dialogType.value, formData.value);
                    }
                    ElMessage.success('操作成功');
                    dialogVisible.value = false;
                    loadData(dialogType.value);
                    loadStats();
                };
                
                onMounted(() => {
                    updateTime();
                    setInterval(updateTime, 1000);
                    loadStats();
                    loadData('budget');
                    loadData('progress');
                    loadData('contract');
                    loadData('expense');
                    loadData('log');
                });
                
                return {
                    currentPage, currentTime, stats, budgets, progress, contracts, expenses, logs,
                    dialogVisible, dialogType, editId, formData, formFields, dialogTitle,
                    formatNumber, showAddDialog, editItem, deleteItem, submitForm
                };
            }
        });
        
        app.use(ElementPlus);
        app.mount('#app');
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    init_db()
    print("🚀 工程造价成本建档系统启动中...")
    print("📍 访问地址: http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
