import sys
import re


def fix_ly(src, dst):

    with open(src, "r", encoding="utf-8") as f:
        data = f.read()


    # 修正 LilyPond tempo 錯誤
    data = re.sub(
        r'\\midi\s*\{\s*\\context\s*\{\s*\\Score\s*tempoWholesPerMinute\s*=\s*#\(ly:make-moment\s+\d+\s+\d+\)\}\s*\}',
        r'\\midi { \tempo 4 = 84 }',
        data
    )


    # 確保有 version
    if "\\version" not in data:
        data = '\\version "2.24.0"\n\n' + data


    with open(dst, "w", encoding="utf-8") as f:
        f.write(data)



if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(
            "Usage: python ly_fix_v1.py input.ly output.ly"
        )
        sys.exit(1)


    fix_ly(
        sys.argv[1],
        sys.argv[2]
    )

    print(
        "LY fix complete:",
        sys.argv[2]
    )