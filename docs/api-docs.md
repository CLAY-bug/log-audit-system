# 后端 API 设计（第 1 周初稿）

所有接口前缀：`/api/v1`
- 鉴权：使用 Bearer token（后续可换正式 JWT），`Authorization: Bearer <token>`。
- 角色：`admin` > `auditor` > `user`，不同接口注明权限。

## Auth
### POST /auth/login
- Body: `{ "username": "alice", "password": "***" }`
- Response: `{ "access_token": "...", "token_type": "bearer", "user": {"id":1,"username":"alice","role":"admin"} }`
- 错误：401 未认证 / 422 参数错误。

### GET /auth/me
- 说明：读取当前登录用户信息。
- 鉴权：登录可用。

## Admin（可选：第一周先占位）
### GET /admin/users
- 角色：admin
- Query: `page`、`size`
- Response: 用户列表 + 分页信息。

### POST /admin/users
- 角色：admin
- Body: `{ "username": "bob", "password": "123456", "role": "auditor" }`
- Response: 新用户信息或 id。

### PATCH /admin/users/{id}
- 角色：admin
- Body: 可更新 `password`、`role`、`status`。

### GET /admin/config
- 角色：admin
- 返回：配置列表（retention_days、alert_threshold_login_fail 等）。

### PUT /admin/config
- 角色：admin
- Body: `[{ "config_key": "retention_days", "config_value": "90" }]`

## 日志 Logs
### POST /logs
- 角色：admin/auditor/user 均可写（按业务控制）。
- Body 示例：
```json
{
  "source": "WEB_APP",
  "level": "ERROR",
  "message": "user login failed",
  "ip": "192.168.0.1",
  "user_name": "alice",
  "timestamp": "2025-11-28T10:20:30Z",
  "raw_data": "原始日志文本"
}
```
- 说明：必填 `source`,`level`,`timestamp`,`message`；时间使用 ISO8601。
- Response: `{ "id": 1001 }`

### POST /logs/upload
- 角色：admin/auditor
- Content-Type: multipart/form-data
- Form: `file`（日志文件）、`source`（WEB_APP/NETWORK/...）
- Response: `{ "inserted": 1200, "failed": 3 }`

### GET /logs
- 角色：admin/auditor；user 仅可查自己相关（后续可按需求限制）。
- Query: `start_time`、`end_time`、`levels`（多选，逗号分隔）、`source`、`ip`、`keyword`、`page`（默认1）、`size`（默认20）。
- Response: 列表 + 分页。

### GET /logs/{id}
- 角色：admin/auditor
- Response: 单条日志详情。

### GET /logs/export
- 角色：admin/auditor
- 说明：复用 /logs 查询条件，返回 CSV 文件流（列：timestamp, level, source, ip, user_name, message, raw_data）。

## 告警 Alerts
### GET /alerts
- 角色：admin/auditor
- Query: `start_time`、`end_time`、`rule_code`、`severity`、`status`、`page`、`size`。
- Response: 告警列表。

### GET /alerts/{id}
- 角色：admin/auditor
- Response: 告警详情（含 related_ip/related_user/log_count/triggered_at/description）。

### PATCH /alerts/{id}
- 角色：admin/auditor
- Body: `{ "status": "processing" | "resolved" }`
- 说明：更新状态，并记录 operation_log。

## 统计 Stats
### GET /stats/logs-by-time
- 角色：admin/auditor
- Query: `start_time`、`end_time`、`bucket`（hour/day）、`source` 可选。
- Response: `[ { "bucket": "2025-11-28T10:00", "count": 120 }, ... ]`

### GET /stats/logs-by-level
- 角色：admin/auditor
- Response: `{ "INFO": 1000, "WARN": 120, "ERROR": 45, "FATAL": 3 }`

## 操作审计 Operation Logs
### GET /operation-logs
- 角色：admin/auditor
- Query: `start_time`、`end_time`、`user_id`、`action`、`page`、`size`
- Response: 审计记录列表（包含 user_id、action、ip、created_at、detail）。

## 错误格式约定
- 未认证：`401 { "detail": "Not authenticated" }`
- 权限不足：`403 { "detail": "Admin only" }`
- 参数错误：`422 { "detail": "..." }`
