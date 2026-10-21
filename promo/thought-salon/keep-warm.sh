#!/usr/bin/env bash
# 思想会客厅(nuwa-h5) Render 免费版「保活」脚本 —— 只在投放期间使用！
#
# 背景：Render 免费实例闲置约 15 分钟会休眠；再被访问时冷启动约 10–60 秒，
#       用户扫码思想海报后会先看到 Render 默认启动页（SERVICE WAKING UP…）。
# 本脚本间隔性 ping 健康接口 /api/persons，让实例保持「热」，避开冷启动。
#
# ⚠️ 额度红线（重要）：
#   Render 免费额度是「账号级」750 实例小时/月，账号下所有 Web 服务共享。
#   nuwa-h5 与 director-salon 若同时长期保活必然超额度、当月被停。
#   ⇒ 同一时间只保活正在投放的那一个服务；投放结束立即 stop。
#
# 用法：
#   ./keep-warm.sh start    后台保活（keep-warm.pid / keep-warm.log）
#   ./keep-warm.sh stop     停止
#   ./keep-warm.sh status   查看状态与最近日志
#   ./keep-warm.sh once     只 ping 一次（测试用）
#
# 可调参数（环境变量）：
#   URL=...       默认 https://nuwa-h5.onrender.com/api/persons
#   INTERVAL=600  间隔秒（须 < 900s 休眠阈值，留余量）
#   LOG=...       日志文件，默认 keep-warm.log
set -u

URL="${URL:-https://nuwa-h5.onrender.com/api/persons}"
INTERVAL="${INTERVAL:-600}"
LOG="${LOG:-keep-warm.log}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$HERE/keep-warm.pid"

ping_once(){ curl -s -m 20 -o /dev/null -w "%{http_code}" "$URL"; }

run(){
  echo "[keep-warm] start $(date '+%F %T')  url=$URL  interval=${INTERVAL}s" >> "$LOG"
  while true; do
    code="$(ping_once)"
    echo "$(date '+%F %T')  GET $URL  -> $code" >> "$LOG"
    sleep "$INTERVAL"
  done
}

case "${1:-start}" in
  start)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "已在运行 PID $(cat "$PIDFILE")"; exit 0; fi
    nohup "$0" __run >/dev/null 2>&1 &
    echo $! > "$PIDFILE"
    echo "已启动 PID $(cat "$PIDFILE")｜日志 $HERE/$LOG｜间隔 ${INTERVAL}s"
    echo "提醒：投放结束请执行  $0 stop"
    ;;
  __run) run ;;
  stop)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      kill "$(cat "$PIDFILE")" 2>/dev/null; rm -f "$PIDFILE"; echo "已停止"
    else
      rm -f "$PIDFILE"; echo "未在运行"; fi
    ;;
  status)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "运行中 PID $(cat "$PIDFILE")"; else echo "未运行"; fi
    echo "--- 最近日志 ---"; tail -n 5 "$HERE/$LOG" 2>/dev/null || echo "(无日志)"
    ;;
  once)  echo "$(date '+%F %T') once -> $(ping_once)"; ;;
  *)     echo "用法: $0 [start|stop|status|once]"; ;;
esac
