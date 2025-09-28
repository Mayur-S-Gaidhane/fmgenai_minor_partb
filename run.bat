@echo off
setlocal enabledelayedexpansion
pushd %~dp0

echo [RUN] Q1: Multilingual ^& Code-Switch (baseline)
python -m src.evaluate_q1 --config config.yaml
if errorlevel 1 goto :error

echo [RUN] Q1: Mitigation (6-item subset)
python -m src.evaluate_q1 --config config.yaml --mitigate
if errorlevel 1 goto :error

echo [RUN] Q2: Robustness to Messy Inputs (full)
python -m src.evaluate_q2 --config config.yaml --intervention prompt
if errorlevel 1 goto :error

echo [DONE] See results\ and plots\
popd
goto :eof

:error
echo [ERROR] A command failed. Check above logs.
popd
exit /b 1
