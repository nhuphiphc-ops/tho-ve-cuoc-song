@echo off
chcp 65001 > nul
title Cap Nhat Tho - Tho Ve Cuoc Song

echo.
echo   ====================================================
echo      CAP NHAT BAI THO - THO VE CUOC SONG
echo      Website: https://tho-ve-cuoc-song.vercel.app
echo   ====================================================
echo.

REM --- Chuyen den thu muc du an ---
cd /d "E:\THO VE CUOC SONG"

echo [Buoc 1/4] Kiem tra file Excel...
if not exist "Tho_chiet_ly_cuoc_song_FullVersion.xlsx" (
    echo.
    echo   [LOI] Khong tim thay file Excel!
    echo   Vui long dat file Excel dung vi tri:
    echo   E:\THO VE CUOC SONG\Tho_chiet_ly_cuoc_song_FullVersion.xlsx
    echo.
    pause
    exit /b 1
)
echo   OK - Da tim thay file Excel.
echo.

echo [Buoc 2/4] Chuyen doi du lieu Excel sang JSON...
python convert.py
if %errorlevel% neq 0 (
    echo.
    echo   [LOI] Qua trinh chuyen doi that bai!
    echo   - Hay kiem tra xem Python da duoc cai dat chua
    echo   - Hay kiem tra lai dinh dang file Excel
    echo.
    pause
    exit /b 1
)
echo   OK - Da tao data.json thanh cong.
echo.

echo [Buoc 3/4] Dang tai du lieu len GitHub...

REM Lay ngay gio hien tai lam commit message
for /f "tokens=1-3 delims=/ " %%a in ('echo %date%') do set NGAY=%%a/%%b/%%c
for /f "tokens=1-2 delims=: " %%a in ('echo %time%') do set GIO=%%a:%%b
set COMMIT_MSG=Cap nhat bai tho moi: %NGAY% %GIO%

git add Tho_chiet_ly_cuoc_song_FullVersion.xlsx data.json tieng_trung.json kinh_dich.json

git diff --quiet --cached
if %errorlevel% equ 0 (
    echo   Khong co thay doi moi nao de cap nhat.
    echo   Du lieu website dang la phien ban moi nhat roi!
    goto DONE_NO_CHANGE
)

git commit -m "%COMMIT_MSG%"

git push origin main
if %errorlevel% neq 0 (
    echo.
    echo   [LOI] Khong the day du lieu len GitHub!
    echo   Vui long kiem tra ket noi internet va thu lai.
    echo.
    pause
    exit /b 1
)
echo   OK - Da day du lieu len GitHub thanh cong.
echo.

echo [Buoc 4/4] Hoan tat!
echo.
echo   ====================================================
echo      THANH CONG!
echo      Vercel dang tu dong deploy website...
echo      Website se cap nhat sau khoang 30-60 giay.
echo.
echo      Xem ket qua tai:
echo      https://tho-ve-cuoc-song.vercel.app
echo   ====================================================
echo.
echo   Bam phim bat ky de dong cua so...
pause > nul
exit /b 0

:DONE_NO_CHANGE
echo.
echo   ====================================================
echo      Website dang la phien ban moi nhat!
echo      https://tho-ve-cuoc-song.vercel.app
echo   ====================================================
echo.
echo   Bam phim bat ky de dong cua so...
pause > nul
