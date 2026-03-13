#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE = '/home/node/.openclaw/workspace';
const BACKUP_DIR = path.join(WORKSPACE, 'backups');
const RETENTION_COUNT = 7;  // 保留最近 N 個備份

// 创建备份目录
if (!fs.existsSync(BACKUP_DIR)) {
  fs.mkdirSync(BACKUP_DIR, { recursive: true });
}

// 生成备份文件名
const now = new Date();
const timestamp = now.toISOString().replace(/[:.]/g, '-').split('T')[0] + 
                  '-' + String(now.getHours()).padStart(2, '0');
const backupFile = path.join(BACKUP_DIR, `backup-${timestamp}.tar.gz`);

try {
  // 执行备份
  console.log(`[Backup] Starting backup at ${now.toISOString()}`);
  const excludeArgs = [
    'node_modules',
    '.git',
    'backups',
    '*.lock',
    '.DS_Store'
  ].map(e => `--exclude=${e}`).join(' ');

  const cmd = `tar -C ${path.dirname(WORKSPACE)} ${excludeArgs} -czf ${backupFile} ${path.basename(WORKSPACE)}`;
  execSync(cmd, { stdio: 'inherit' });

  // 获取备份文件大小
  const stats = fs.statSync(backupFile);
  const sizeInMB = (stats.size / 1024 / 1024).toFixed(2);
  console.log(`[Backup] ✅ Backup completed: ${backupFile} (${sizeInMB}MB)`);

  // 清理过期备份（保留最近 N 個）
  const files = fs.readdirSync(BACKUP_DIR)
    .filter(f => f.startsWith('backup-') && f.endsWith('.tar.gz'))
    .map(f => ({
      name: f,
      path: path.join(BACKUP_DIR, f),
      time: fs.statSync(path.join(BACKUP_DIR, f)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time);  // 按時間降序排序（最新的在前）

  let deletedCount = 0;
  
  // 保留最近 RETENTION_COUNT 個，刪除其餘的
  if (files.length > RETENTION_COUNT) {
    const filesToDelete = files.slice(RETENTION_COUNT);  // 取第 N 個之後的所有備份
    
    filesToDelete.forEach(file => {
      fs.unlinkSync(file.path);
      console.log(`[Backup] 🗑️  Deleted old backup: ${file.name}`);
      deletedCount++;
    });
  }

  console.log(`[Backup] 📊 Total backups: ${files.length - deletedCount}, Deleted: ${deletedCount}`);
  process.exit(0);

} catch (error) {
  console.error(`[Backup] ❌ Error: ${error.message}`);
  process.exit(1);
}
