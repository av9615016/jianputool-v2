# ==========================================
# JianpuTool
# jianpu_ly output cleaner V1
#
# 修正:
# jianpu_ly 產生 ly 前面混入文字
# Wrong / warning / log
#
# MusicXML -> jianpu_ly -> clean ly -> LilyPond
# ==========================================


import sys
import os


VERSION = r'\version "2.20.0"'



def clean_ly(input_file, output_file):

    print("==============================")
    print(" JIANPU LY CLEANER V1")
    print("==============================")


    if not os.path.exists(input_file):

        raise FileNotFoundError(
            input_file
        )


    # 讀取原始 ly

    with open(
        input_file,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        text = f.read()



    # 移除 BOM

    text = text.replace(
        "\ufeff",
        ""
    )


    lines = text.splitlines()



    # 找真正 LilyPond 開始

    start = None


    for i, line in enumerate(lines):

        s = line.strip()


        if (
            s.startswith("\\version")
            or
            s.startswith("\\paper")
            or
            s.startswith("\\score")
            or
            s.startswith("#(")
        ):

            start = i
            break



    if start is None:

        print(
            "⚠ 找不到 LilyPond 開頭"
        )

        start = 0


    else:

        print(
            "LilyPond start line:",
            start
        )



    clean_lines = lines[start:]



    # 檢查 version

    has_version = False


    for line in clean_lines:

        if line.strip().startswith(
            "\\version"
        ):

            has_version = True
            break



    if not has_version:

        print(
            "加入 LilyPond version"
        )

        clean_lines.insert(
            0,
            VERSION
        )



    # 輸出

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(clean_lines)
        )



    print(
        "完成:",
        output_file
    )



    # 顯示第一行檢查

    print("------------------------------")

    with open(
        output_file,
        "r",
        encoding="utf-8"
    ) as f:

        for i in range(5):

            line = f.readline()

            if not line:
                break

            print(
                line.rstrip()
            )

    print("------------------------------")




if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用:"
        )

        print(
            "python jianpu_ly_cleaner.py input.ly output.ly"
        )

        sys.exit(1)



    clean_ly(
        sys.argv[1],
        sys.argv[2]
    )