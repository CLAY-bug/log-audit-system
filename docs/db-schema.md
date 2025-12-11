# 数据库表结构（初稿）

> MySQL 8.0 / InnoDB / utf8mb4。枚举值为推荐初稿，后续可以改查表或扩展。

## users（用户与角色）
| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT UNSIGNED | PK AUTO_INCREMENT | 主键 |
| username | VARCHAR(64) | NOT NULL UNIQUE | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希，建议 bcrypt/PBKDF2 |
| role | ENUM('admin','auditor','user') | NOT NULL DEFAULT 'user' | 角色 |
| status | TINYINT | NOT NULL DEFAULT 1 | 1=active,0=disabled |
| last_login_at | DATETIME | NULL | 上次登录时间 |
| last_login_ip | VARCHAR(45) | NULL | 上次登录 IP |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

索引：UNIQUE(username)，BTREE(role,status)。

## logs（统一日志）
| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT UNSIGNED | PK AUTO_INCREMENT | 主键 |
| source | ENUM('WEB_APP','NETWORK','ROUTER','FIREWALL','DATABASE','OTHER') | NOT NULL | 日志来源 |
| level | ENUM('DEBUG','INFO','WARN','ERROR','FATAL') | NOT NULL DEFAULT 'INFO' | 日志级别 |
| timestamp | DATETIME | NOT NULL | 原始日志时间 |
| ip | VARCHAR(45) | NULL | 相关 IP（源/目的按约定） |
| user_name | VARCHAR(64) | NULL | 日志中出现的用户名（字符串） |
| message | VARCHAR(1024) | NOT NULL | 简要信息，便于列表展示 |
| raw_data | TEXT | NULL | 原始日志内容 |
| ingest_type | ENUM('file','api','manual') | NOT NULL DEFAULT 'file' | 日志接入方式 |
| parse_status | ENUM('ok','failed') | NOT NULL DEFAULT 'ok' | 解析是否成功 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 写入时间 |

索引：BTREE(timestamp)、BTREE(level)、BTREE(source)、BTREE(ip)、BTREE(user_name)、组合 BTREE(timestamp, source, level)。

## alerts（告警记录）
| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT UNSIGNED | PK AUTO_INCREMENT | 主键 |
| rule_code | VARCHAR(64) | NOT NULL | 规则编码（程序内部使用，如 BF_LOGIN、ERROR_RATE） |
| rule_name | VARCHAR(128) | NOT NULL | 规则名称（展示用） |
| severity | ENUM('low','medium','high','critical') | NOT NULL DEFAULT 'medium' | 告警等级 |
| status | ENUM('new','processing','resolved') | NOT NULL DEFAULT 'new' | 告警状态 |
| triggered_at | DATETIME | NOT NULL | 首次触发时间 |
| related_ip | VARCHAR(45) | NULL | 关联 IP |
| related_user | VARCHAR(64) | NULL | 关联用户名字符 |
| log_count | INT UNSIGNED | NOT NULL DEFAULT 0 | 关联日志数量 |
| description | VARCHAR(512) | NULL | 告警描述/备注 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

索引：BTREE(triggered_at)、BTREE(rule_code)、BTREE(status)、组合 BTREE(severity, status, triggered_at)。

## operation_log（操作审计日志）
| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT UNSIGNED | PK AUTO_INCREMENT | 主键 |
| user_id | BIGINT UNSIGNED | NOT NULL | FK -> users.id |
| action | VARCHAR(64) | NOT NULL | 动作类型，如 LOGIN / UPLOAD_LOG / EXPORT / UPDATE_CONFIG |
| detail | VARCHAR(1024) | NULL | 动作详情，JSON 或文本 |
| ip | VARCHAR(45) | NULL | 操作来源 IP |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |

索引：BTREE(user_id, created_at)、BTREE(action, created_at)。

## config（系统配置 KV）
| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT UNSIGNED | PK AUTO_INCREMENT | 主键 |
| config_key | VARCHAR(128) | NOT NULL UNIQUE | 如 retention_days, alert_threshold_login_fail |
| config_value | VARCHAR(512) | NOT NULL | 配置值，统一字符串存储 |
| description | VARCHAR(255) | NULL | 说明 |
| updated_by | BIGINT UNSIGNED | NULL | 最后修改人 users.id |
| updated_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

## 约束关系
- operation_log.user_id -> users.id（ON DELETE CASCADE / ON UPDATE CASCADE）。
- config.updated_by -> users.id（ON DELETE SET NULL / ON UPDATE CASCADE）。
- alerts 目前只记录 related_ip/related_user，并不强 FK 到 logs，便于支持外部事件。

## 其他约定
- 日志表按 timestamp 做范围查询，后续可按月分表或设置 retention_days 清理策略。
- 默认字符集使用 utf8mb4，排序规则 utf8mb4_unicode_ci。
