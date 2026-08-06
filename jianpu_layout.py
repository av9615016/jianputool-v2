# ==========================================================
# JianpuTool Professional MVP 2.1
# jianpu_layout.py
#
# Professional Jianpu LilyPond Layout
#
# Input:
#     jianpu.ly
#
# Output:
#     professional.ly
#
# ==========================================================


import sys
import os



# ==========================================================
# Layout Template
# ==========================================================


HEADER = r"""
\version "2.26.0"


#(set-global-staff-size 18)


\paper {

  #(set-paper-size "a4")

  top-margin = 15\mm
  bottom-margin = 15\mm
  left-margin = 18\mm
  right-margin = 18\mm

}


\header {

 title = "JianpuTool AI Jianpu"

 subtitle = "Professional Edition"

 composer = "JianpuTool"

}


"""



# ==========================================================
# Format Settings
# ==========================================================


LAYOUT = r"""

\layout {

 indent = 0

 ragged-right = ##f

}


"""



# ==========================================================
# Add page break control
# ==========================================================


def optimize_score(content):


    content=content.replace(

        "\\score",

        """
\\pageBreak

\\score

"""

    )


    return content



# ==========================================================
# Split long lines
# ==========================================================


def split_long_lines(content):


    lines=[]


    for line in content.splitlines():


        if len(line)>120:


            parts=line.split()


            buffer=""


            for p in parts:


                if len(buffer)+len(p)>100:


                    lines.append(buffer)

                    buffer=p


                else:


                    buffer+=" "+p



            if buffer:

                lines.append(buffer)



        else:


            lines.append(line)



    return "\n".join(lines)



# ==========================================================
# Main
# ==========================================================


def main():


    if len(sys.argv)<3:


        print(

            "python jianpu_layout.py input.ly output.ly"

        )

        sys.exit()



    inp=sys.argv[1]

    out=sys.argv[2]



    print(
        "讀取:",
        inp
    )



    with open(
        inp,
        "r",
        encoding="utf-8"
    ) as f:


        content=f.read()



    print(
        "套用專業排版..."
    )



    content=split_long_lines(
        content
    )


    content=optimize_score(
        content
    )



    final=(

        HEADER

        +

        content

        +

        LAYOUT

    )



    with open(
        out,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            final
        )



    print(
        "完成:",
        out
    )



if __name__=="__main__":

    main()