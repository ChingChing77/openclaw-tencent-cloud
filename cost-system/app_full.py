import os
import csv
import io
from flask import Flask, render_template_string, request, jsonify, make_response
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_NAME = "cost_system_full.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 消息表
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, title TEXT, content TEXT, type TEXT, is_read INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    # 预算表
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (id INTEGER PRIMARY KEY, project_name TEXT, cost_type TEXT, budget_amount REAL, actual_amount REAL, difference REAL, status TEXT DEFAULT '进行中', remark TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    # 进度表
    c.execute('''CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY, project_name TEXT, responsible_person TEXT, start_date TEXT, end_date TEXT, progress_percent INTEGER DEFAULT 0, status TEXT DEFAULT '进行中', remark TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    # 合同表
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (id INTEGER PRIMARY KEY, contract_name TEXT, contract_amount REAL, sign_date TEXT, party_a TEXT, party_b TEXT, contract_status TEXT DEFAULT '执行中', remark TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    # 报销表
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, expense_type TEXT, amount REAL, expense_date TEXT, applicant TEXT, approval_status TEXT DEFAULT '待审批', approver TEXT, remark TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    # 设置表
    c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, category TEXT, setting_key TEXT, setting_value TEXT, enabled INTEGER DEFAULT 1, UNIQUE(category, setting_key))''')
    # 日志表
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, username TEXT, action TEXT, detail TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    
    # 默认设置
    c.execute("SELECT COUNT(*) FROM settings")
    if c.fetchone()[0] == 0:
        settings = [
            ('预算管理','初步预算编制','启用'),('预算管理','预算调整管理','启用'),('预算管理','预算追踪与分析','启用'),('预算管理','预算审核与批准','启用'),
            ('成本控制','成本数据收集','启用'),('成本控制','成本分析报告','启用'),('成本控制','成本超支预警','启用'),('成本控制','项目成本总结','启用'),
            ('合同管理','合同模板管理','启用'),('合同管理','合同执行监督','启用'),('合同管理','合同变更记录','启用'),('合同管理','合同到期提醒','启用'),
            ('项目进度管理','进度计划编制','启用'),('项目进度管理','进度跟踪与更新','启用'),('项目进度管理','进度偏差分析','启用'),('项目进度管理','项目里程碑管理','启用'),
        ]
        c.executemany("INSERT OR IGNORE INTO settings (category, setting_key, setting_value) VALUES (?,?,?)", settings)
    
    # 示例数据
    c.execute("SELECT COUNT(*) FROM budgets")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO budgets (id, project_name, cost_type, budget_amount, actual_amount, difference, status, remark, created_at) VALUES (?,?,?,?,?,?,?,?,datetime('now'))", [(1,'土建工程','人工费',500000,550000,50000,'进行中','人工超支'),(2,'设备采购','设备费',300000,280000,-20000,'已完成','节省'),(3,'安装工程','材料费',200000,220000,20000,'进行中','涨价')])
        c.executemany("INSERT INTO progress (id, project_name, responsible_person, start_date, end_date, progress_percent, status, remark, created_at) VALUES (?,?,?,?,?,?,?,?,datetime('now'))", [(1,'住宅楼A栋','张伟','2024-01-01','2024-12-31',50,'进行中',''),(2,'商业综合体','李强','2024-03-01','2025-06-30',25,'进行中','')])
        c.executemany("INSERT INTO contracts (id, contract_name, contract_amount, sign_date, party_a, party_b, contract_status, remark, created_at) VALUES (?,?,?,?,?,?,?,?,datetime('now'))", [(1,'钢材采购合同',2000000,'2024-01-15','建筑公司','钢材供应商','执行中',''),(2,'施工合同',5000000,'2024-02-01','开发商','建筑公司','执行中','')])
        c.executemany("INSERT INTO expenses (id, expense_type, amount, expense_date, applicant, approval_status, approver, remark, created_at) VALUES (?,?,?,?,?,?,?,?,datetime('now'))", [(1,'差旅费',3500,'2024-01-15','张伟','已审批','李强',''),(2,'餐饮费',2800,'2024-01-20','李强','待审批','','')])
        c.executemany("INSERT INTO messages (id, title, content, type, is_read, created_at) VALUES (?,?,?,?,?,datetime('now'))", [(1,'进度提醒','项目进度更新','系统通知',0),(2,'超支预警','土建工程超支5%','预警',0)])
        conn.commit()
    conn.close()

def db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = lambda c, r: dict(zip([d[0] for d in c.description], r))
    return conn

def log_act(a, d):
    conn = db()
    conn.execute("INSERT INTO logs (username, action, detail) VALUES (?,?,?)", ('admin', a, str(d)))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/stats')
def stats():
    conn = db()
    b = conn.execute("SELECT COUNT(*),SUM(budget_amount),SUM(actual_amount) FROM budgets").fetchone()
    p = conn.execute("SELECT COUNT(*),AVG(progress_percent) FROM progress").fetchone()
    c1 = conn.execute("SELECT COUNT(*),SUM(contract_amount) FROM contracts").fetchone()
    e = conn.execute("SELECT COUNT(*),SUM(amount) FROM expenses WHERE approval_status='已审批'").fetchone()
    m = conn.execute("SELECT COUNT(*) FROM messages WHERE is_read=0").fetchone()
    conn.close()
    return jsonify({
        'budget_count': b[0] or 0, 'total_budget': b[1] or 0, 'total_actual': b[2] or 0,
        'progress_count': p[0] or 0, 'avg_progress': round(p[1] or 0, 1),
        'contract_count': c1[0] or 0, 'contract_total': c1[1] or 0,
        'expense_count': e[0] or 0, 'expense_total': e[1] or 0,
        'unread_messages': m[0] or 0
    })

@app.route('/api/<table>', methods=['GET'])
def get_list(table):
    return jsonify([r for r in db().execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()])

@app.route('/api/<table>', methods=['POST'])
def addItem(table):
    d = request.json
    cols_map = {
        'budgets': ['project_name', 'cost_type', 'budget_amount', 'actual_amount', 'difference', 'status', 'remark'],
        'progress': ['project_name', 'responsible_person', 'start_date', 'end_date', 'progress_percent', 'status', 'remark'],
        'contracts': ['contract_name', 'contract_amount', 'sign_date', 'party_a', 'party_b', 'contract_status', 'remark'],
        'expenses': ['expense_type', 'amount', 'expense_date', 'applicant', 'approval_status', 'approver', 'remark'],
        'messages': ['title', 'content', 'type']
    }
    cols = cols_map.get(table, [])
    conn = db()
    conn.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", [d.get(x) for x in cols])
    conn.commit()
    conn.close()
    log_act(f'添加{table}', str(d))
    return jsonify({'success': True})

@app.route('/api/<table>/<int:id>', methods=['PUT'])
def updItem(table, id):
    d = request.json
    conn = db()
    keys = ','.join([f"{k}=?" for k in d.keys()])
    conn.execute(f"UPDATE {table} SET {keys} WHERE id=?", list(d.values()) + [id])
    conn.commit()
    conn.close()
    log_act(f'更新{table}', str(id))
    return jsonify({'success': True})

@app.route('/api/<table>/<int:id>', methods=['DELETE'])
def delItem(table, id):
    conn = db()
    conn.execute(f"DELETE FROM {table} WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_act(f'删除{table}', str(id))
    return jsonify({'success': True})

@app.route('/api/messages/<int:id>/read', methods=['PUT'])
def mark_message_read(id):
    conn = db()
    conn.execute("UPDATE messages SET is_read=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    r = db().execute("SELECT * FROM settings ORDER BY category,id").fetchall()
    result = {}
    for x in r:
        result.setdefault(x['category'], []).append(x)
    return jsonify(result)

@app.route('/api/settings', methods=['POST'])
def upd_setting():
    d = request.json
    conn = db()
    conn.execute("UPDATE settings SET setting_value=?,enabled=? WHERE category=? AND setting_key=?", (d['setting_value'], d.get('enabled', 1), d['category'], d['setting_key']))
    conn.commit()
    conn.close()
    log_act('更新设置', f"{d['category']}-{d['setting_key']}")
    return jsonify({'success': True})

@app.route('/api/budgets/export', methods=['GET'])
def exp_budgets():
    rows = db().execute("SELECT * FROM budgets").fetchall()
    si = io.StringIO()
    w = csv.writer(si)
    w.writerow(['ID', '项目', '类型', '预算', '实际', '差异', '状态', '备注'])
    for r in rows:
        w.writerow([r['id'], r['project_name'], r['cost_type'], r['budget_amount'], r['actual_amount'], r['difference'], r['status'], r['remark']])
    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=budgets.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

HTML = '''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><title>工程造价成本建档系统 V2.0</title>
<link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css">
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script><script src="https://unpkg.com/element-plus"></script><script src="https://unpkg.com/axios/dist/axios.min.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#f0f2f5}.header{background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);color:#fff;padding:20px 30px;display:flex;justify-content:space-between;align-items:center}.header h1{font-size:22px}.container{display:flex;min-height:calc(100vh - 70px)}.sidebar{width:220px;background:#fff;box-shadow:2px 0 8px rgba(0,0,0,.05)}.sidebar li{padding:14px 24px;cursor:pointer;border-left:3px solid transparent;transition:.3s;display:flex;align-items:center;gap:10px}.sidebar li:hover{background:#f5f7fa}.sidebar li.active{background:#f0f5ff;border-left-color:#0f3460;color:#0f3460;font-weight:600}.content{flex:1;padding:24px}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:30px}.stat{background:#fff;padding:24px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.05)}.stat h3{font-size:14px;color:#909;margin-bottom:12px}.stat .v{font-size:32px;font-weight:700;color:#303}.page{font-size:22px;font-weight:600;margin-bottom:24px}.bar{display:flex;gap:12px;margin-bottom:20px}.table{background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.05)}.setting{background:#fff;padding:20px;border-radius:12px;margin-bottom:16px}.setting h3{font-size:16px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #eee}.item{display:flex;justify-content:space-between;padding:16px 0;border-bottom:1px solid #f5f5f5}.item:last-child{border:none}</style></head>
<body><div id="app"><div class="header"><div><h1>🏗️ 工程造价成本建档系统</h1><small style="opacity:0.8">V2.0 完整版</small></div><div><el-badge :value="s.unread_messages" v-if="s.unread_messages"><span>🔔</span></el-badge> <span style="margin-left:20px">{{t}}</span></div></div>
<div class="container"><ul class="sidebar"><li :class="{active:p==='home'}" @click="p='home'">📊 首页</li><li :class="{active:p==='messages'}" @click="p='messages'">🔔 新消息</li><li :class="{active:p==='budget'}" @click="p='budget'">💰 成本预算</li><li :class="{active:p==='progress'}" @click="p='progress'">📈 项目进度</li><li :class="{active:p==='control'}" @click="p='control'">⚙️ 控制中心</li><li :class="{active:p==='contract'}" @click="p='contract'">📄 合同管理</li><li :class="{active:p==='expense'}" @click="p='expense'">💳 费用报销</li><li :class="{active:p==='log'}" @click="p='log'">📝 日志</li></ul>
<div class="content"><!--首页--><div v-if="p==='home'"><div class="page">📊 数据概览</div><div class="stats"><div class="stat" style="border-top:3px solid #409eff"><h3>预算项目</h3><div class="v">{{s.budget_count}}</div><small>¥{{n(s.total_budget)}}</small></div><div class="stat" style="border-top:3px solid #e6a23c"><h3>实际支出</h3><div class="v">¥{{n(s.total_actual)}}</div><small>执行{{pr(s.total_actual,s.total_budget)}}%</small></div><div class="stat" style="border-top:3px solid #67c23a"><h3>项目数</h3><div class="v">{{s.progress_count}}</div><small>进度{{s.avg_progress}}%</small></div><div class="stat" style="border-top:3px solid #9b59b6"><h3>合同</h3><div class="v">{{s.contract_count}}</div><small>¥{{n(s.contract_total)}}</small></div><div class="stat" style="border-top:3px solid #f56c6c"><h3>待审批</h3><div class="v">{{s.expense_count}}</div><small>已批¥{{n(s.expense_total)}}</small></div></div></div>
<!--消息--><div v-if="p==='messages'"><div class="page">🔔 新消息通知</div><div class="bar"><el-button type="primary" @click="sh('message')">➕ 添加</el-button></div><div class="table"><el-table :data="messages" stripe><el-table-column prop="id" label="ID" width="60"></el-table-column><el-table-column prop="title" label="标题"></el-table-column><el-table-column prop="content" label="内容"></el-table-column><el-table-column prop="type" label="类型"></el-table-column><el-table-column prop="is_read" label="状态" width="100"><template #default="s"><el-tag :type="s.row.is_read?'success':'warning'">{{s.row.is_read?'已读':'未读'}}</el-tag></template></el-table-column><el-table-column label="操作"><template #default="s"><el-button size="small" @click="rd(s.row.id)">标为已读</el-button></template></el-table-column></el-table></div></div>
<!--预算--><div v-if="p==='budget'"><div class="page">💰 成本预算管理</div><div class="bar"><el-button type="primary" @click="sh('budget')">➕ 添加</el-button><el-button @click="ex">📥 导出</el-button></div><div class="table"><el-table :data="budgets" stripe><el-table-column prop="id" label="ID" width="60"></el-table-column><el-table-column prop="project_name" label="项目"></el-table-column><el-table-column prop="cost_type" label="类型"></el-table-column><el-table-column label="预算"><template #default="s">¥{{n(s.row.budget_amount)}}</template></el-table-column><el-table-column label="实际"><template #default="s">¥{{n(s.row.actual_amount)}}</template></el-table-column><el-table-column label="差异"><template #default="s"><span :style="{color:s.row.difference>0?'#f56c6c':'#67c23a'}">{{s.row.difference>0?'+':''}}{{n(s.row.difference)}}</span></template></el-table-column><el-table-column prop="status" label="状态"><template #default="s"><el-tag :type="s.row.status==='已完成'?'success':'primary'">{{s.row.status}}</el-tag></template></el-table-column><el-table-column label="操作" width="150"><template #default="s"><el-button size="small" @click="ed('budget',s.row)">编辑</el-button><el-button size="small" type="danger" @click="dl('budget',s.row.id)">删</el-button></template></el-table-column></el-table></div></div>
<!--进度--><div v-if="p==='progress'"><div class="page">📈 项目进度追踪</div><div class="bar"><el-button type="primary" @click="sh('progress')">➕ 新增</el-button></div><div class="table"><el-table :data="progress" stripe><el-table-column prop="id" label="ID" width="60"></el-table-column><el-table-column prop="project_name" label="项目"></el-table-column><el-table-column prop="responsible_person" label="负责人"></el-table-column><el-table-column prop="start_date" label="开始"></el-table-column><el-table-column prop="end_date" label="结束"></el-table-column><el-table-column label="进度"><template #default="s"><el-progress :percentage="s.row.progress_percent" :status="s.row.progress_percent===100?'success':''"></el-progress></template></el-table-column><el-table-column label="操作" width="150"><template #default="s"><el-button size="small" @click="ed('progress',s.row)">编辑</el-button><el-button size="small" type="danger" @click="dl('progress',s.row.id)">删</el-button></template></el-table-column></el-table></div></div>
<!--控制中心--><div v-if="p==='control'"><div class="page">⚙️ 控制中心</div><div v-for="(items,cat) in settings" :key="cat"><div class="setting"><h3>{{cat}}</h3><div class="item" v-for="s in items" :key="s.id"><span>{{s.setting_key}}</span><el-switch v-model="s.enabled" :active-value="1" :inactive-value="0" @change="upSt(cat,s.setting_key,s.enabled)"></el-switch></div></div></div></div>
<!--合同--><div v-if="p==='contract'"><div class="page">📄 合同管理</div><div class="bar"><el-button type="primary" @click="sh('contract')">➕ 添加</el-button></div><div class="table"><el-table :data="contracts" stripe><el-table-column prop="id" label="ID" width="60"></el-table-column><el-table-column prop="contract_name" label="合同名称"></el-table-column><el-table-column label="金额"><template #default="s">¥{{n(s.row.contract_amount)}}</template></el-table-column><el-table-column prop="sign_date" label="签订日期"></el-table-column><el-table-column prop="party_a" label="甲方"></el-table-column><el-table-column prop="party_b" label="乙方"></el-table-column><el-table-column prop="contract_status" label="状态"><template #default="s"><el-tag :type="s.row.contract_status==='执行中'?'success':'info'">{{s.row.contract_status}}</el-tag></template></el-table-column><el-table-column label="操作" width="150"><template #default="s"><el-button size="small" @click="ed('contract',s.row)">编辑</el-button><el-button size="small" type="danger" @click="dl('contract',s.row.id)">删</el-button></template></el-table-column></el-table></div></div>
<!--报销--><div v-if="p==='expense'"><div class="page">💳 费用报销记录</div><div class="bar"><el-button type="primary" @click="sh('expense')">➕ 添加</el-button></div><div class="table"><el-table :data="expenses" stripe><el-table-column prop="id" label="ID" width="60"></el-table-column><el-table-column prop="expense_type" label="类型"></el-table-column><el-table-column label="金额"><template #default="s">¥{{n(s.row.amount)}}</template></el-table-column><el-table-column prop="expense_date" label="日期"></el-table-column><el-table-column prop="applicant" label="申请人"></el-table-column><el-table-column prop="approval_status" label="状态"><template #default="s"><el-tag :type="s.row.approval_status==='已审批'?'success':'warning'">{{s.row.approval_status}}</el-tag></template></el-table-column><el-table-column label="操作" width="150"><template #default="s"><el-button size="small" @click="ed('expense',s.row)">编辑</el-button><el-button size="small" type="danger" @click="dl('expense',s.row.id)">删</el-button></template></el-table-column></el-table></div></div>
<!--日志--><div v-if="p==='log'"><div class="page">📝 日志消息</div><div class="table"><el-table :data="logs" stripe><el-table-column prop="id" label="ID" width="60"></el-table-column><el-table-column prop="action" label="操作"></el-table-column><el-table-column prop="detail" label="详情"></el-table-column><el-table-column prop="created_at" label="时间"></el-table-column></el-table></div></div></div></div>
<el-dialog v-model="d" :title="dt" width="500px"><el-form :model="f"><el-form-item v-for="(v,k) in fd[t]" :key="k" :label="v"><el-input v-if="v!='状态'&&v!='类型'" v-model="f[k]"></el-input><el-select v-else v-model="f[k]"><el-option v-for="o in(v==='状态'?['进行中','已完成']:v==='类型'?['通知','预警','提醒']:['执行中','已完成','待审批','已审批'])":key="o" :label="o" :value="o"></el-option></el-select></el-form-item></el-form><template #footer><el-button @click="d=false">取消</el-button><el-button type="primary" @click="sb">确定</el-button></template></el-dialog></div>
<script>const {createApp,ref,onMounted}=Vue;const app=createApp({setup(){const p=ref('home'),t=ref(''),s=ref({}),d=ref(!1),tmode=ref(''),editId=ref(null),f=ref({}),budgets=ref([]),progress=ref([]),contracts=ref([]),expenses=ref([]),messages=ref([]),logs=ref([]),settings=ref({});
const fd={budgets:{project_name:'项目名称',cost_type:'费用类型',budget_amount:'预算金额',actual_amount:'实际金额',difference:'差异',status:'状态',remark:'备注'},progress:{project_name:'项目名称',responsible_person:'负责人',start_date:'开始日期',end_date:'结束日期',progress_percent:'进度%',status:'状态',remark:'备注'},contracts:{contract_name:'合同名称',contract_amount:'合同金额',sign_date:'签订日期',party_a:'甲方',party_b:'乙方',contract_status:'状态',remark:'备注'},expenses:{expense_type:'费用类型',amount:'金额',expense_date:'报销日期',applicant:'申请人',approval_status:'状态',approver:'审批人',remark:'备注'},messages:{title:'标题',content:'内容',type:'类型'}};
const n=num=>num?Number(num).toLocaleString():'0';const pr=(a,b)=>b?Math.round(a/b*100):0;const load=async()=>{s.value=(await axios('/api/stats')).data;tmode.value='';d.value=!1;editId.value=null;f.value={};[budgets.value,progress.value,contracts.value,expenses.value,messages.value,logs.value,settings.value]=(await Promise.all([axios('/api/budgets'),axios('/api/progress'),axios('/api/contracts'),axios('/api/expenses'),axios('/api/messages'),axios('/api/logs'),axios('/api/settings')])).map(r=>r.data)};
const sh=type=>{tmode.value=type;editId.value=null;f.value={};Object.keys(fd[type]).forEach(k=>f.value[k]='');d.value=!0;return tmode.value};const ed=(type,row)=>{tmode.value=type;editId.value=row.id;f.value={...row};d.value=!0};const dl=async(type,id)=>{await ElMessageBox.confirm('确认删除?');await axios.delete(`/api/${type}/${id}`);ElMessage.success('删除成功');load();p.value==='home'?load():0};
const sb=async()=>{const type=tmode.value;editId.value?await axios.put(`/api/${type}/${editId.value}`,f.value):await axios.post(`/api/${type}`,f.value);ElMessage.success('成功');d.value=!1;load()};
const rd=async id=>{await axios.put(`/api/messages/${id}/read`);load()};const upSt=async(cat,key,val)=>{await axios.post('/api/settings',{category:cat,setting_key:key,enabled:val})};const ex=()=>window.open('/api/budgets/export');
onMounted(()=>{load();setInterval(()=>{t.value=new Date().toLocaleString('zh-CN')},1000)});return{p,t,s,d,f,fd,tmode,budgets,progress,contracts,expenses,messages,logs,settings,n,pr,sh,ed,dl,sb,rd,upSt,ex}});app.use(ElementPlus);app.mount('#app');</script></body></html>'''

if __name__ == '__main__':
    init_db()
    print("🚀 完整版系统启动...")
    print("📍 访问: http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
