USE log_audit;

CREATE TABLE `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希，如 bcrypt/PBKDF2',
  `role` ENUM('admin','auditor','user') NOT NULL DEFAULT 'user' COMMENT '角色',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1=active,0=disabled',
  `last_login_at` DATETIME NULL,
  `last_login_ip` VARCHAR(45) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_username` (`username`),
  KEY `idx_users_role_status` (`role`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户与角色';

CREATE TABLE `logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `source` ENUM('WEB_APP','NETWORK','ROUTER','FIREWALL','DATABASE','OTHER') NOT NULL COMMENT '日志来源',
  `level` ENUM('DEBUG','INFO','WARN','ERROR','FATAL') NOT NULL DEFAULT 'INFO' COMMENT '日志级别',
  `timestamp` DATETIME NOT NULL COMMENT '原始日志时间',
  `ip` VARCHAR(45) NULL COMMENT '相关 IP（源/目的按约定）',
  `user_name` VARCHAR(64) NULL COMMENT '日志中出现的用户名（字符串）',
  `message` VARCHAR(1024) NOT NULL COMMENT '简要信息，便于列表展示',
  `raw_data` TEXT NULL COMMENT '原始日志内容',
  `ingest_type` ENUM('file','api','manual') NOT NULL DEFAULT 'file' COMMENT '日志接入方式',
  `parse_status` ENUM('ok','failed') NOT NULL DEFAULT 'ok' COMMENT '解析是否成功',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_logs_timestamp` (`timestamp`),
  KEY `idx_logs_level` (`level`),
  KEY `idx_logs_source` (`source`),
  KEY `idx_logs_ip` (`ip`),
  KEY `idx_logs_user_name` (`user_name`),
  KEY `idx_logs_time_source_level` (`timestamp`, `source`, `level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='统一日志表';

CREATE TABLE `alerts` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `rule_code` VARCHAR(64) NOT NULL COMMENT '规则编码，程序内部使用',
  `rule_name` VARCHAR(128) NOT NULL COMMENT '规则名称，展示用',
  `severity` ENUM('low','medium','high','critical') NOT NULL DEFAULT 'medium' COMMENT '告警等级',
  `status` ENUM('new','processing','resolved') NOT NULL DEFAULT 'new' COMMENT '告警状态',
  `triggered_at` DATETIME NOT NULL COMMENT '首次触发时间',
  `related_ip` VARCHAR(45) NULL COMMENT '关联 IP',
  `related_user` VARCHAR(64) NULL COMMENT '关联用户名字符',
  `log_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '关联日志数量',
  `description` VARCHAR(512) NULL COMMENT '告警描述/备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_alerts_triggered_at` (`triggered_at`),
  KEY `idx_alerts_rule_code` (`rule_code`),
  KEY `idx_alerts_status` (`status`),
  KEY `idx_alerts_sev_status_time` (`severity`, `status`, `triggered_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='告警记录';

CREATE TABLE `operation_log` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '操作用户 ID',
  `action` VARCHAR(64) NOT NULL COMMENT '动作类型，如 LOGIN / UPLOAD_LOG / EXPORT / UPDATE_CONFIG',
  `detail` VARCHAR(1024) NULL COMMENT '动作详情，JSON 或文本',
  `ip` VARCHAR(45) NULL COMMENT '操作来源 IP',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_oplog_user_time` (`user_id`, `created_at`),
  KEY `idx_oplog_action_time` (`action`, `created_at`),
  CONSTRAINT `fk_oplog_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作审计日志';

CREATE TABLE `config` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `config_key` VARCHAR(128) NOT NULL COMMENT '如 retention_days, alert_threshold_login_fail',
  `config_value` VARCHAR(512) NOT NULL COMMENT '配置值，统一用字符串存储',
  `description` VARCHAR(255) NULL COMMENT '说明',
  `updated_by` BIGINT UNSIGNED NULL COMMENT '最后修改人 users.id',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`),
  KEY `idx_config_updated_by` (`updated_by`),
  CONSTRAINT `fk_config_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置';
