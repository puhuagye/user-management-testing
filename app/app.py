
"""
用户管理系统 - Flask 路由层
============================
这个文件只负责"接待 HTTP 请求"：
  1. 接收浏览器/curl 发来的请求
  2. 调用 models.py 里的函数操作数据库
  3. 把结果转成 JSON 返回

面试时可以说：路由层和数据层分离，换数据库不用改接口代码
"""
import logging

from flask import Flask, request, jsonify, render_template
from app.models import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user,
)

# 创建本模块专用的 logger，__name__ 的值是 "app.app"
# 这样日志里能看到是哪个文件输出的
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.json.ensure_ascii = False
@app.route('/', methods=['GET'])
def index():
  """根路径 — API 欢迎页"""
  return jsonify({
      'code': 200,
      'message': '欢迎使用用户管理系统API',
      'api_docs': {
          'GET /api/users': '查询全部用户',
          'GET /api/users/<id>': '查询单个用户',
          'POST /api/users': '新增用户',
          'PUT /api/users/<id>': '修改用户',
          'DELETE /api/users/<id>': '删除用户',
      }
  })
# ============================================================
# 页面路由：返回 HTML 页面（给浏览器看的，不是 JSON）
# 注意：页面路由用 /users，API 路由用 /api/users，两者不冲突
# ============================================================

@app.route('/users')
def user_list_page():
    """用户列表页面 — 浏览器访问 http://127.0.0.1:5000/users"""
    return render_template('index.html')


@app.route('/users/create')
def user_create_page():
    """新增用户页面 — 浏览器访问 http://127.0.0.1:5000/users/create"""
    return render_template('create.html')


@app.route('/users/<int:user_id>/edit')
def user_edit_page(user_id):
    """编辑用户页面 — 浏览器访问 http://127.0.0.1:5000/users/3/edit"""
    return render_template('edit.html')

# ============================================================
# 接口1：查全部用户
# ============================================================
@app.route('/api/users', methods=['GET'])
def list_users():
    """
        处理 GET /api/users 请求
        返回数据库中所有用户，按 ID 倒序排列（最新添加的排最上面）
        """
    users = get_all_users()
    return jsonify({
        'code': 200,
        'message': '查询成功',
        'data': users
    })
# ============================================================
# 接口2：查单个用户
# ============================================================
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
        处理 GET /api/users/3 这样的请求
        <int:user_id> 把 URL 里的数字（比如 3）转成整数，传给 user_id 参数
        """
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({
            'code': 404,
            'message':'用户不存在',
            'data': None,
        })
    return jsonify({
        'code': 200,
        'message':'查询成功',
        'data': user,
    })
# ============================================================
# 接口3：新增用户
# ============================================================
@app.route('/api/users', methods=['POST'])
def add_user():
  """
  处理 POST /api/users 请求
  请求体里要带 JSON 数据：{"name": "张三", "email": "z3@test.com", "phone": "13800000000"}
  """
  # 第1步：用 request.get_json() 拿到请求体里的 JSON 数据
  data = request.get_json()

  # 第2步：判空 — 如果请求体是空的，或者没传 JSON，直接拒绝
  # 为什么判空？后面代码要用 data.get()，如果 data 是 None 就会报错
  if not data:
      logger.warning("新增用户 — 请求体为空")
      #  ↑ WARNING：请求不太对劲，但程序本身没坏
      return jsonify({
          'code': 400,                       # 400 = 客户端请求有问题
          'message': '请求体不能为空，请传 JSON 数据',
          'data': None,
      })

  # 第3步：从 JSON 里取 name 和 email（必填），phone（选填）
  # .get("key", "默认值") 的好处：key 不存在也不会报错，而是返回默认值
  # .strip() 去掉用户不小心敲的首尾空格
  name = data.get('name', '').strip()
  email = data.get('email', '').strip()
  phone = (data.get('phone') or '').strip() or None
  #                            ↑ "" or None → None
  # 用户没填手机号就存 None（数据库里的 NULL），不存空字符串

  # 第4步：校验必填字段 — name 和 email 不能为空
  if not name or not email:
      logger.warning(f"新增用户 — 缺少必填字段 name={repr(name)} email={repr(email)}")
      #  ↑ f"...{变量}..." = f-string，把变量值嵌入字符串
      #  ↑ repr() = 显示变量的原始样子，空字符串会显示成 ''
      return jsonify({
          'code': 400,
          'message': '姓名和邮箱不能为空',
          'data': None,
      })

  # 第5步：调用 models 层写入数据库
  try:
      new_id = create_user(name, email, phone)
      logger.info(f"新增用户成功 — ID={new_id} name={name} email={email}")
      #  ↑ INFO：正常的业务流程完成了，记一笔
      return jsonify({
          'code': 201,                       # 201 = 资源创建成功
          'message': '用户创建成功',
          'data': {'id': new_id},
      })
  except Exception as e:
      # 如果数据库报错（比如邮箱重复），捕获异常，返回友好提示
      logger.error(f"新增用户失败 — {e}", exc_info=True)
      #  ↑ ERROR：出错了，功能没完成
      #  ↑ exc_info=True：把完整的报错堆栈也记到日志里，能看到是哪一行炸的
      return jsonify({
          'code': 500,                       # 500 = 服务器内部错误
          'message': f'创建失败：{str(e)}',
          'data': None,
      })
# ============================================================
# 接口4：修改用户
# ============================================================
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
  """
  处理 PUT /api/users/3 请求
  请求体里传要修改的字段：{"name": "张三丰", "phone": "13900000000"}
  只更新传了值的字段，没传的不改
  """
  # 第1步：拿 JSON 数据
  data = request.get_json()
  if not data:
      return jsonify({
          'code': 400,
          'message': '请求体不能为空',
          'data': None,
      })

  # 第2步：取出要改的字段（都是选填，改哪个传哪个）
  name = data.get('name', '').strip() or None
  email = data.get('email', '').strip() or None
  phone = (data.get('phone') or '').strip() or None
  # 注意：这里用 or None 是因为 models 层的 update_user 函数
  # 靠"是不是 None"来判断要不要改这个字段

  # 第3步：调用 models 层修改
  # update_user 返回 True（改到了）或 False（用户不存在 / 没传字段）
  try:
      success = update_user(user_id, name=name, email=email, phone=phone)
  except Exception as e:
      # 数据库异常（如邮箱重复），返回友好 JSON 而不是让 Flask 崩成 HTML
      logger.error(f"修改用户失败 — {e}", exc_info=True)
      return jsonify({
          'code': 500,
          'message': f'修改失败：{str(e)}',
          'data': None,
      })

  if not success:
      return jsonify({
          'code': 404,
          'message': '修改失败：用户不存在或没有要修改的字段',
          'data': None,
      })

  return jsonify({
      'code': 200,
      'message': '修改成功',
      'data': {'id': user_id},
  })
# ============================================================
# 接口5：删除用户
# ============================================================
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
  """
  处理 DELETE /api/users/3 请求
  删除指定 ID 的用户
  """
  # 调用 models 层删除
  # delete_user 返回 True（删掉了）或 False（用户不存在）
  success = delete_user(user_id)

  if not success:
      logger.warning(f"删除失败 — ID={user_id} 不存在")
      return jsonify({
          'code': 404,
          'message': '删除失败：用户不存在',
          'data': None,
      })

  logger.info(f"删除成功 — ID={user_id}")
  return jsonify({
      'code': 200,
      'message': '删除成功',
      'data': {'id': user_id},
  })