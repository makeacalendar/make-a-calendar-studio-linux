#!/usr/bin/env bash
set -euo pipefail
GUI_PYTHON="${GUI_PYTHON:-python3}"
mkdir -p screenshots
openbox >/tmp/mcs-openbox.log 2>&1 &
wm_pid=$!
sleep 1
cleanup() { kill "$wm_pid" 2>/dev/null || true; }
trap cleanup EXIT
pages=(
  "overview:01-overview"
  "designer:02-calendar-designer"
  "year:03-year-planner"
  "print:04-print-studio"
  "fiscal:05-fiscal-studio"
  "payroll:06-payroll-shifts"
  "dates:07-date-tools"
  "resources:08-online-resources"
)
for item in "${pages[@]}"; do
  page="${item%%:*}"
  image="${item#*:}"
  MCS_START_PAGE="$page" PYTHONPATH=src "$GUI_PYTHON" -m make_a_calendar_studio \
    >"/tmp/mcs-${page}.log" 2>&1 &
  app_pid=$!
  window_id=""
  for attempt in $(seq 1 20); do
    if ! kill -0 "$app_pid" 2>/dev/null; then cat "/tmp/mcs-${page}.log"; exit 1; fi
    window_id=$(xdotool search --onlyvisible --name "Make a Calendar Studio" 2>/dev/null | head -n 1 || true)
    if [[ -n "$window_id" ]]; then break; fi
    sleep 1
  done
  if [[ -z "$window_id" ]]; then cat "/tmp/mcs-${page}.log"; exit 1; fi
  wmctrl -ia "$window_id"
  wmctrl -ir "$window_id" -b add,maximized_vert,maximized_horz || true
  sleep 1
  xdotool mousemove 1420 980
  scrot -u "screenshots/${image}.png"
  xdotool windowclose "$window_id" || kill "$app_pid" 2>/dev/null || true
  wait "$app_pid" 2>/dev/null || true
done
