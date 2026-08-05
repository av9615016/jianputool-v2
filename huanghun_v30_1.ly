\version "2.20.0"
#(set-global-staff-size 20)

% un-comment the next line to remove Lilypond tagline:
% \header { tagline="" }

% comment out the next line if you're debugging jianpu-ly
% (but best leave it un-commented in production, since
% the point-and-click locations won't go to the user input)
\pointAndClickOff

\paper {
  print-all-headers = ##t %% allow per-score headers

  % un-comment the next line for A5:
  % #(set-default-paper-size "a5" )

  % un-comment the next line for no page numbers:
  % print-page-number = ##f

  % un-comment the next 3 lines for a binding edge:
  % two-sided = ##t
  % inner-margin = 20\mm
  % outer-margin = 10\mm

  % un-comment the next line for a more space-saving header layout:
  % scoreTitleMarkup = \markup { \center-column { \fill-line { \magnify #1.5 { \bold { \fromproperty #'header:dedication } } \magnify #1.5 { \bold { \fromproperty #'header:title } } \fromproperty #'header:composer } \fill-line { \fromproperty #'header:instrument \fromproperty #'header:subtitle \smaller{\fromproperty #'header:subsubtitle } } } }
}

%% 2-dot and 3-dot articulations
#(append! default-script-alist
   (list
    `(two-dots
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,#{ \markup \override #'(font-encoding . latin1) \center-align \bold ":" #})
           (padding . 0.20)
           (avoid-slur . inside)
           (side-axis . ,Y)
           (direction . ,UP)))))
#(append! default-script-alist
   (list
    `(three-dots
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,#{ \markup \override #'(font-encoding . latin1) \center-align \bold "⋮" #})
           (padding . 0.30)
           (avoid-slur . inside)
           (side-axis . ,Y)
           (direction . ,UP)))))
"two-dots" =
#(make-articulation 'two-dots)

"three-dots" =
#(make-articulation 'three-dots)

\layout {
  \context {
    \Score
    scriptDefinitions = #default-script-alist
  }
}

note-mod =
#(define-music-function
     (text note)
     (markup? ly:music?)
   #{
     \tweak NoteHead.stencil #ly:text-interface::print
     \tweak NoteHead.text
        \markup \lower #0.5 \sans \bold #text
     \tweak Rest.stencil #ly:text-interface::print
     \tweak Rest.text
        \markup \lower #0.5 \sans \bold #text
     #note
   #})
#(define (flip-beams grob)
   (ly:grob-set-property!
    grob 'stencil
    (ly:stencil-translate
     (let* ((stl (ly:grob-property grob 'stencil))
            (centered-stl (ly:stencil-aligned-to stl Y DOWN)))
       (ly:stencil-translate-axis
        (ly:stencil-scale centered-stl 1 -1)
        (* (- (car (ly:stencil-extent stl Y)) (car (ly:stencil-extent centered-stl Y))) 0) Y))
     (cons 0 -0.8))))

%=======================================================
#(define-event-class 'jianpu-grace-curve-event 'span-event)

#(define (add-grob-definition grob-name grob-entry)
   (set! all-grob-descriptions
         (cons ((@@ (lily) completize-grob-entry)
                (cons grob-name grob-entry))
               all-grob-descriptions)))

#(define (jianpu-grace-curve-stencil grob)
   (let* ((elts (ly:grob-object grob 'elements))
          (refp-X (ly:grob-common-refpoint-of-array grob elts X))
          (X-ext (ly:relative-group-extent elts refp-X X))
          (refp-Y (ly:grob-common-refpoint-of-array grob elts Y))
          (Y-ext (ly:relative-group-extent elts refp-Y Y))
          (direction (ly:grob-property grob 'direction RIGHT))
          (x-start (* 0.5 (+ (car X-ext) (cdr X-ext))))
          (y-start (+ (car Y-ext) 0.32))
          (x-start2 (if (eq? direction RIGHT)(+ x-start 0.5)(- x-start 0.5)))
          (x-end (if (eq? direction RIGHT)(+ (cdr X-ext) 0.2)(- (car X-ext) 0.2)))
          (y-end (- y-start 0.5))
          (stil (ly:make-stencil `(path 0.1
                                        (moveto ,x-start ,y-start
                                         curveto ,x-start ,y-end ,x-start ,y-end ,x-start2 ,y-end
                                         lineto ,x-end ,y-end))
                                  X-ext
                                  Y-ext))
          (offset (ly:grob-relative-coordinate grob refp-X X)))
     (ly:stencil-translate-axis stil (- offset) X)))

#(add-grob-definition
  'JianpuGraceCurve
  `(
     (stencil . ,jianpu-grace-curve-stencil)
     (meta . ((class . Spanner)
              (interfaces . ())))))

#(define jianpu-grace-curve-types
   '(
      (JianpuGraceCurveEvent
       . ((description . "Used to signal where curve encompassing music start and stop.")
          (types . (general-music jianpu-grace-curve-event span-event event))
          ))
      ))

#(set!
  jianpu-grace-curve-types
  (map (lambda (x)
         (set-object-property! (car x)
           'music-description
           (cdr (assq 'description (cdr x))))
         (let ((lst (cdr x)))
           (set! lst (assoc-set! lst 'name (car x)))
           (set! lst (assq-remove! lst 'description))
           (hashq-set! music-name-to-property-table (car x) lst)
           (cons (car x) lst)))
    jianpu-grace-curve-types))

#(set! music-descriptions
       (append jianpu-grace-curve-types music-descriptions))

#(set! music-descriptions
       (sort music-descriptions alist<?))


#(define (add-bound-item spanner item)
   (if (null? (ly:spanner-bound spanner LEFT))
       (ly:spanner-set-bound! spanner LEFT item)
       (ly:spanner-set-bound! spanner RIGHT item)))

jianpuGraceCurveEngraver =
#(lambda (context)
   (let ((span '())
         (finished '())
         (current-event '())
         (event-start '())
         (event-stop '()))
     `(
       (listeners
        (jianpu-grace-curve-event .
          ,(lambda (engraver event)
             (if (= START (ly:event-property event 'span-direction))
                 (set! event-start event)
                 (set! event-stop event)))))

       (acknowledgers
        (note-column-interface .
          ,(lambda (engraver grob source-engraver)
             (if (ly:spanner? span)
                 (begin
                  (ly:pointer-group-interface::add-grob span 'elements grob)
                  (add-bound-item span grob)))
             (if (ly:spanner? finished)
                 (begin
                  (ly:pointer-group-interface::add-grob finished 'elements grob)
                  (add-bound-item finished grob)))))
        (inline-accidental-interface .
          ,(lambda (engraver grob source-engraver)
             (if (ly:spanner? span)
                 (begin
                  (ly:pointer-group-interface::add-grob span 'elements grob)))
             (if (ly:spanner? finished)
                 (ly:pointer-group-interface::add-grob finished 'elements grob))))
        (script-interface .
          ,(lambda (engraver grob source-engraver)
             (if (ly:spanner? span)
                 (begin
                  (ly:pointer-group-interface::add-grob span 'elements grob)))
             (if (ly:spanner? finished)
                 (ly:pointer-group-interface::add-grob finished 'elements grob)))))
       
       (process-music .
         ,(lambda (trans)
            (if (ly:stream-event? event-stop)
                (if (null? span)
                    (ly:warning "No start to this curve.")
                    (begin
                     (set! finished span)
                     (ly:engraver-announce-end-grob trans finished event-start)
                     (set! span '())
                     (set! event-stop '()))))
            (if (ly:stream-event? event-start)
                (begin
                 (set! span (ly:engraver-make-grob trans 'JianpuGraceCurve event-start))
                 (set! event-start '())))))
       
       (stop-translation-timestep .
         ,(lambda (trans)
            (if (and (ly:spanner? span)
                     (null? (ly:spanner-bound span LEFT)))
                (ly:spanner-set-bound! span LEFT
                  (ly:context-property context 'currentMusicalColumn)))
            (if (ly:spanner? finished)
                (begin
                 (if (null? (ly:spanner-bound finished RIGHT))
                     (ly:spanner-set-bound! finished RIGHT
                       (ly:context-property context 'currentMusicalColumn)))
                 (set! finished '())
                 (set! event-start '())
                 (set! event-stop '())))))
       
       (finalize
        (lambda (trans)
          (if (ly:spanner? finished)
              (begin
               (if (null? (ly:spanner-bound finished RIGHT))
                   (set! (ly:spanner-bound finished RIGHT)
                         (ly:context-property context 'currentMusicalColumn)))
               (set! finished '())))))
       )))

jianpuGraceCurveStart =
#(make-span-event 'JianpuGraceCurveEvent START)

jianpuGraceCurveEnd =
#(make-span-event 'JianpuGraceCurveEvent STOP)
%===========================================================

%{ The jianpu-ly input was:
OctavesAfter
title=Music21 Fragment
composer=Music21
instrument=
4/4
4=80
7''q   
1#   ~
]
1#q   
]
1#   ~
5#   
5#   ~
]
5#q   
3'   ~
]
3'q   
]
3'   
5#   ~
5#   ~
]
5#q   
3''   ~
]
3''q   
]
5'#   
7   ~
7   ~
]
7q   
7'   ~
]
7'q   
]
7'   
1'#   ~
1'#   ~
]
1'#q   
5#   ~
]
5#q   
]
1#   
5#   
1'#   ~
]
1'#q   
5#   ~
]
5#q   
]
5'#   
1'#   
4'#   ~
]
4'#q   
1'#   ~
]
1'#q   
]
3''b   
3''b   
3'b   ~
]
3'bq   
1''#   ~
]
1''#q   ~
]
1''#   
3'b   ~
3'b   ~
]
3'bq   
3'b   ~
]
3'bq   
]
7   
5'#   
3''b   ~
]
3''bq   ~
3''b   ~
]
3''bq   
]
3''b   
3'b   
7'   ~
]
7'q   
1''#   ~
]
1''#q   
]
5#   
5#   ~
5#   ~
]
5#q   
3   ~
]
3q   
]
4#   
5#   
5#   ~
]
5#q   ~
5#   ~
]
5#q   
]
3b   
3'b   
3b   ~
]
3bq   
3b   ~
]
3bq   
]
3b   ~
3b   
3b   ~
]
3bq   
7,   ~
]
7,q   
]
3'b   ~
3'b   
3b   ~
]
3bq   
3b   ~
]
3bq   
]
5#   
3b   ~
3b   ~
]
3bq   
3b   ~
]
3bq   
]
4#   
3b   
3'b   ~
]
3'bq   
3''b   ~
]
3''bq   
]
5'#   
3''b   
3'b   ~
]
3'bq   
3'b   ~
]
3'bq   
]
1''#   
7'   
3'b   ~
]
3'bq   
2   ~
]
2q   
]
3b   
3b   ~
3b   ~
]
3bq   
3b   ~
]
3bq   ~
]
3b   
4#   
3b   ~
]
3bq   
3b   ~
]
3bq   
]
5#   
3'b   
5#   ~
]
5#q   ~
5#   ~
]
5#q   
]
3   
7   
1'#   ~
]
1'#q   
5#   ~
]
5#q   ~
]
5#   
7,   
5#   ~
]
5#q   
5#   ~
]
5#q   ~
]
5#   
5#   
5#   ~
]
5#q   
7   ~
]
7q   
]
7   
1'#   
4#   ~
]
4#q   
7   ~
]
7q   
]
3'b   
1'#   
7   ~
]
7q   
1''#   ~
]
1''#q   ~
]
1''#   
7,   
4#   ~
]
4#q   
7   ~
]
7q   
]
3   
5#   
5#   ~
]
5#q   
5#   ~
]
5#q   
]
3'b   
5#   ~
5#   ~
]
5#q   
6   ~
]
6q   
]
1#   
3'   
3   ~
]
3q   
7,   ~
]
7,q   
]
7,   
5#   ~
5#   ~
]
5#q   
7,   ~
]
7,q   
]
5#   
3'   
4'#   ~
]
4'#q   
5#   ~
]
5#q   
]
5#   ~
3''   
5#   ~
]
5#q   
3'b   ~
]
3'bq   
]
5'#   ~
5'#   
5'#   ~
]
5'#q   
5'#   ~
]
5'#q   
]
3'b   
3'b   
4#   ~
]
4#q   
4#   ~
]
4#q   ~
]
4#   
7   
1'#   ~
]
1'#q   
1'#   ~
]
1'#q   
]
1'#   
6,   
1'#   ~
]
1'#q   
7,   ~
]
7,q   ~
]
4#   
4#   
4#   ~
]
4#q   
5'#   ~
]
5'#q   
]
5'#   
7,   
5#   ~
]
5#q   
3   ~
]
3q   
]
5#   
4#   
5#   ~
]
5#q   
7   ~
]
7q   
]
5#   
6   
7   ~
]
7q   
3'   ~
]
3'q   ~
]
3'   
1#   
3   ~
]
3q   
3   ~
]
3q   
]
1''#   
7,   
1#   ~
]
1#q   
5#   ~
]
5#q   
]
3'b   
3'b   
3'b   ~
]
3'bq   
3'b   ~
]
3'bq   
]
7'   
3'b   
3'b   ~
]
3'bq   ~
3'b   ~
]
3'bq   
]
1#   
5#   
5#   ~
]
5#q   
5#   ~
]
5#q   
]
1#   
3'   
5#   ~
]
5#q   
1#   ~
]
1#q   
]
3'   
3'   
5#   ~
]
5#q   
3'   ~
]
3'q   
]
5#   
1#   
3'b   ~
]
3'bq   
1#   ~
]
1#q   
]
3'b   
3b   
3b   ~
]
3bq   
6   ~
]
6q   
]
6   
4'#   
3'b   ~
]
3'bq   
6   ~
]
6q   
]
7,   
4#   ~
4#   ~
]
4#q   
7'   ~
]
7'q   
]
7   
3''b   
5'#   ~
]
5'#q   
3'   ~
]
3'q   ~
]
3'   
5'#   
3''   ~
]
3''q   
5'#   ~
]
5'#q   
]
4'#   ~
1#   
3'   ~
]
3'q   ~
4'   ~
]
4'q   
]
3'b   
3'b   
3'b   ~
]
3'bq   
1'#   ~
]
1'#q   
]
5#   
5'#   
3b   ~
]
3bq   ~
3b   ~
]
3bq   
]
3b   
5'#   
1'#   ~
]
1'#q   
4'#   ~
]
4'#q   
]
3'   
4'#   
1'#   ~
]
1'#q   
4'#   ~
]
4'#q   
]
1''#   
3   
4#   ~
]
4#q   
3   ~
]
3q   
]
7'   
5#   
3b   ~
]
3bq   
5#   ~
]
5#q   ~
]
5#   
3b   
5,#   ~
]
5,#q   
3'b   ~
]
3'bq   
]
1'#   
3b   
1#   ~
]
1#q   
5'#   ~
]
5'#q   
]
5'#   
7   
3b   ~
]
3bq   
3b   ~
]
3bq   
]
7,   
5#   
2   ~
]
2q   
3   ~
]
3q   
]
3   
3   
4#   ~
]
4#q   ~
4#   ~
]
4#q   
]
3b   
4#   
3b   ~
]
3bq   
3b   ~
]
3bq   
]
7,   
1#   ~
1#   ~
]
1#q   
1#   ~
]
1#q   
]
3   
5#   
3'b   ~
]
3'bq   
1#   ~
]
1#q   
]
1#   
1#   ~
1#   ~
]
1#q   
5,#   ~
]
5,#q   
]
5#   
3   
3   ~
]
3q   
4#   ~
]
4#q   
]
4#   
7   
4#   ~
]
4#q   
5'#   ~
]
5'#q   
]
5'#   
7,   
4#   ~
]
4#q   
4#   ~
]
4#q   
]
4#   
5'#   
7   ~
]
7q   
1'#   ~
]
1'#q   
]
1'#   
7   
7   ~
]
7q   
4#   ~
]
4#q   
]
7   
5#   
7   ~
]
7q   
5#   ~
]
5#q   
]
4#   
7   
7   ~
]
7q   
1#   ~
]
1#q   
]
1'#   
3   
1#   ~
]
1#q   
3   ~
]
3q   
]
1#   
6   
7,   ~
]
7,q   
1#   ~
]
1#q   
]
3b   
1#   
3'b   ~
]
3'bq   
1#   ~
]
1#q   
]
1#   
1'#   ~
1'#   ~
]
1'#q   
3'b   ~
]
3'bq   
]
3b   
4#   
5'#   ~
]
5'#q   
5'#   ~
]
5'#q   
]
5#   
5'#   ~
5'#   ~
]
5'#q   
5#   ~
]
5#q   
]
5#   
5#   
4#   ~
]
4#q   
4#   ~
]
4#q   
]
4#   ~
4#   
5'#   ~
]
5'#q   
5'#   ~
]
5'#q   
]
4#   
7,   
7   ~
]
7q   
1''#   ~
]
1''#q   
]
7   
7   
4#   ~
]
4#q   
5,#   ~
]
5,#q   ~
]
5,#   
5#   
4#   ~
]
4#q   
4#   ~
]
4#q   
]
5#   
7   
7   ~
]
7q   ~
7   ~
]
7q   
]
1#   
3'   
1#   ~
]
1#q   
1#   ~
]
1#q   ~
]
1#   
6   
3   ~
]
3q   
3b   ~
]
3bq   ~
]
3b   
6,   
1#   ~
]
1#q   
3b   ~
]
3bq   
]
5,#   
5#   
1#   ~
]
1#q   
1#   ~
]
1#q   
]
1#   
1#   
3'b   ~
]
3'bq   
3b   ~
]
3bq   
]
4#   
4#   
5#   ~
]
5#q   
7,   ~
]
7,q   
]
5#   
3   ~
3   ~
]
3q   
5#   ~
]
5#q   
]
5#   
3   
5#   ~
]
5#q   
7   ~
]
7q   
]
3b   
4#   
5#   ~
]
5#q   
7   ~
]
7q   
]
1''#   
1'#   ~
1'#   ~
]
1'#q   
1'#   ~
]
1'#q   
]
7   
4#   
3   ~
]
3q   
3   ~
]
3q   
]
5#   
5,#   
5#   ~
]
5#q   ~
5#   ~
]
5#q   
]
5'#   
6'   
6   ~
]
6q   ~
6   ~
]
6q   
]
6   
3'   
3'   ~
]
3'q   
7,   ~
]
7,q   
]
7,   
7,   
4#   ~
]
4#q   
5#   ~
]
5#q   
]
3   
4#   
1''#   ~
]
1''#q   
5'#   ~
]
5'#q   
]
7'   
1''#   
4#   ~
]
4#q   
5#   ~
]
5#q   
]
5'#   
5#   
5'#   ~
]
5'#q   
5#   ~
]
5#q   ~
]
5#   
7   
4#   ~
]
4#q   ~
3'b   ~
]
3'bq   
]
7   
1#   ~
1''#   ~
]
1''#q   
1''#   ~
]
1''#q   
]
1'#   
4'#   ~
4'#   ~
]
4'#q   
5#   ~
]
5#q   
]
5#   
5'#   
5#   ~
]
5#q   
3'b   ~
]
3'bq   
]
1#   
1#   
3'b   ~
]
3'bq   
1'#   ~
]
1'#q   
]
1'#   
1#   
3'b   ~
]
3'bq   
7,   ~
]
7,q   
]
3b   ~
3b   
7'   ~
]
7'q   
5'#   ~
]
5'#q   
]
3''   
3'b   ~
3'b   ~
]
3'bq   
5'#   ~
]
5'#q   
]
1''#   
5#   
5#   ~
]
5#q   
1#   ~
]
1#q   ~
]
1#   
1#   
WithStaff NextPart
%}


\score {
<< \override Score.BarNumber #'break-visibility = #center-visible
\override Score.BarNumber #'Y-offset = -1
\set Score.barNumberVisibility = #(every-nth-bar-number-visible 5)

%% === BEGIN JIANPU STAFF ===
    \new RhythmicStaff \with {
    \consists "Accidental_engraver" 
    \consists \jianpuGraceCurveEngraver
   %% Limit space between Jianpu and corresponding-Western staff
   \override VerticalAxisGroup.staff-staff-spacing = #'((minimum-distance . 7) (basic-distance . 7) (stretchability . 0))

    % Get rid of the stave but not the barlines:
    \override StaffSymbol #'line-count = #0 % tested in 2.15.40, 2.16.2, 2.18.0, 2.18.2, 2.20.0 and 2.22.2
    \override BarLine #'bar-extent = #'(-2 . 2) % LilyPond 2.18: please make barlines as high as the time signature even though we're on a RhythmicStaff (2.16 and 2.15 don't need this although its presence doesn't hurt; Issue 3685 seems to indicate they'll fix it post-2.18)
    $(add-grace-property 'Voice 'Stem 'direction DOWN)
    $(add-grace-property 'Voice 'Slur 'direction UP)
    $(add-grace-property 'Voice 'Stem 'length-fraction 0.5)
    $(add-grace-property 'Voice 'Beam 'beam-thickness 0.1)
    $(add-grace-property 'Voice 'Beam 'length-fraction 0.3)
    $(add-grace-property 'Voice 'Beam 'after-line-breaking flip-beams)
    $(add-grace-property 'Voice 'Beam 'Y-offset 2.5)
    $(add-grace-property 'Voice 'NoteHead 'Y-offset 2.5)
    }
    { \new Voice="W" {
    \override Beam #'transparent = ##f
    \override Stem #'direction = #DOWN
    \override Tie #'staff-position = #2.5
    \tupletUp
    \tieUp
    \override Stem #'length-fraction = #0
    \override Beam #'beam-thickness = #0.1
    \override Beam #'length-fraction = #0.5
    \override Beam.after-line-breaking = #flip-beams
    \override Voice.Rest #'style = #'neomensural % this size tends to line up better (we'll override the appearance anyway)
    \override Accidental #'font-size = #-4
    \override TupletBracket #'bracket-visibility = ##t

    \override Staff.TimeSignature #'style = #'numbered
    \override Staff.Stem #'transparent = ##t
     \time 4/4 \tempo 4=80 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "7" b8-\tweak #'X-offset #0.6 ^\two-dots [
]   \note-mod "1" \once \tweak Accidental.extra-offset #'(0 . 0.7)cis4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "1" cis4 ~  \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)gis4
| %{ bar 2: %}
 \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)gis4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "3" e4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8^.[]
}  \note-mod "3" e4^. | %{ bar 3: %}
 \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)gis4
~  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]    \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" e4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" e8-\tweak #'X-offset #0.6 ^\two-dots []
} | %{ bar 4: %}
 \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)gis4^.
 \note-mod "7" b4 ~  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]   \note-mod "7" b4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8^.[]
}  \note-mod "7" b4^.  \note-mod "1" \once \tweak Accidental.extra-offset #'(0 . 0.7)cis4^.
~  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)gis4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "1" \once \tweak Accidental.extra-offset #'(0 . 0.7)cis4
 \note-mod "5" gis4  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "5" gis4^.  \note-mod "1" cis4^.  \note-mod "4" \once \tweak Accidental.extra-offset #'(0 . 0.7)fis4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8^.[
]   \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[]
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4-\tweak #'X-offset #0.6 ^\two-dots 
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]    \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" \once \tweak Accidental.extra-offset #'(0 . 0.7)cis4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis8-\tweak #'X-offset #0.6 ^\two-dots []
~ }   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "3" ees4^. ~  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "7" b4  \note-mod "5" gis4^.   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees8-\tweak #'X-offset #0.6 ^\two-dots [
]  ~   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees8-\tweak #'X-offset #0.6 ^\two-dots []
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "3" ees4^.  \note-mod "7" b4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8^.[
]    \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis8-\tweak #'X-offset #0.6 ^\two-dots []
}  \note-mod "5" gis4  \note-mod "5" gis4 ~  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[]
}  \note-mod "4" \once \tweak Accidental.extra-offset #'(0 . 0.7)fis4
 \note-mod "5" gis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]  ~  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
 \note-mod "3" ees4^.  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "3" ees4 ~  \note-mod "3" ees4  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. []
}  \note-mod "3" ees4^. ~  \note-mod "3" ees4^.  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "5" gis4  \note-mod "3" ees4 ~  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "4" fis4  \note-mod "3" ees4  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]    \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees8-\tweak #'X-offset #0.6 ^\two-dots []
}  \note-mod "5" gis4^.   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" ees4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "7" b4^.  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "2" d4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "2" d8[]
}  \note-mod "3" ees4  \note-mod "3" ees4 ~  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
~ }  \note-mod "3" ees4  \note-mod "4" fis4  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "5" gis4  \note-mod "3" ees4^.  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]  ~  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4
 \note-mod "7" b4  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
~ }  \note-mod "5" gis4  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
~ }  \note-mod "5" gis4  \note-mod "5" gis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[]
}  \note-mod "7" b4  \note-mod "1" cis4^.  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[]
}  \note-mod "3" ees4^.  \note-mod "1" cis4^.  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]    \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis8-\tweak #'X-offset #0.6 ^\two-dots []
~ }   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[]
}  \note-mod "3" e4  \note-mod "5" gis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "3" ees4^.  \note-mod "5" gis4 ~  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "6" a4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "6" a8[]
}  \note-mod "1" cis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4^.
 \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[
]   \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. []
}  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "5" gis4 ~  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. []
}  \note-mod "5" gis4  \note-mod "3" e4^.  \note-mod "4" fis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8^.[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "5" gis4 ~   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "5" gis4^. ~  \note-mod "5" gis4^.  \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "3" ees4^.  \note-mod "3" ees4^.  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[]
~ }  \note-mod "4" fis4  \note-mod "7" b4  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[]
}  \note-mod "1" cis4^.  \note-mod "6" a4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. []
~ }  \note-mod "4" fis4  \note-mod "4" fis4  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "5" gis4^.  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[]
}  \note-mod "5" gis4  \note-mod "4" fis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[]
}  \note-mod "5" gis4  \note-mod "6" a4  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]   \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8^.[]
~ }  \note-mod "3" e4^.  \note-mod "1" cis4  \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[
]   \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[]
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
 \note-mod "3" ees4^.  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "7" b4^.  \note-mod "3" ees4^.  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]  ~  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "1" cis4  \note-mod "5" gis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "1" cis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4^.
 \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "3" e4^.  \note-mod "3" e4^.  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "3" e4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8^.[]
}  \note-mod "5" gis4  \note-mod "1" cis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "3" ees4^.  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
 \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "6" a4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "6" a8[]
}  \note-mod "6" a4  \note-mod "4" fis4^.  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "6" a4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "6" a8[]
}  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "4" fis4 ~  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "7" b4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8^.[]
}  \note-mod "7" b4   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[
]   \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8^.[]
~ }  \note-mod "3" e4^.  \note-mod "5" gis4^.   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" e8-\tweak #'X-offset #0.6 ^\two-dots [
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "4" fis4^. ~  \note-mod "1" cis4  \note-mod "3" e4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8^.[
]  ~  \note-mod "4" \once \tweak Accidental.extra-offset #'(0 . 0.7)f4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" f8^.[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
 \note-mod "3" ees4^.  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[]
}  \note-mod "5" gis4  \note-mod "5" gis4^.  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]  ~  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "3" ees4  \note-mod "5" gis4^.  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "4" \once \tweak Accidental.extra-offset #'(0 . 0.7)fis4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8^.[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4^.
 \note-mod "4" fis4^.  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "4" fis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8^.[]
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4
 \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[]
}  \note-mod "7" b4^.  \note-mod "5" gis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
~ }  \note-mod "5" gis4  \note-mod "3" ees4  \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)gis4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8-\tweak #'X-offset #0.6 _. [
]   \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "1" cis4^.  \note-mod "3" ees4  \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "5" gis4^.  \note-mod "7" b4  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "5" gis4  \note-mod "2" d4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "2" d8[
]   \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[]
}  \note-mod "3" e4  \note-mod "3" e4  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]  ~  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
 \note-mod "4" fis4  \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "1" cis4 ~  \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4
 \note-mod "5" gis4  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "1" cis4  \note-mod "1" cis4 ~  \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "5" gis4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8-\tweak #'X-offset #0.6 _. []
}  \note-mod "5" gis4  \note-mod "3" e4  \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[
]   \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[]
}  \note-mod "4" fis4  \note-mod "7" b4  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "5" gis4^.  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[]
}  \note-mod "4" fis4  \note-mod "5" gis4^.  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]   \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[]
}  \note-mod "1" cis4^.  \note-mod "7" b4  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]   \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[]
}  \note-mod "7" b4  \note-mod "5" gis4  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "4" fis4  \note-mod "7" b4  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "1" cis4^.  \note-mod "3" e4  \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[]
}  \note-mod "1" cis4  \note-mod "6" a4  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. [
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
 \note-mod "1" cis4  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "1" cis4  \note-mod "1" cis4^. ~  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "3" ees4  \note-mod "4" fis4  \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "5" gis4  \note-mod "5" gis4^. ~  \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "5" gis4  \note-mod "5" gis4  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[]
}  \note-mod "4" fis4 ~  \note-mod "4" fis4  \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "4" fis4  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]    \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis8-\tweak #'X-offset #0.6 ^\two-dots []
}  \note-mod "7" b4  \note-mod "7" b4  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "5" gis4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8-\tweak #'X-offset #0.6 _. []
~ }  \note-mod "5" gis4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "5" gis4  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[]
}  \note-mod "5" gis4  \note-mod "7" b4  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[
]  ~  \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[]
}  \note-mod "1" cis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4^.
 \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
~ }  \note-mod "1" cis4  \note-mod "6" a4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[
]   \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
~ }  \note-mod "3" ees4  \note-mod "6" a4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "5" gis4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "5" gis4  \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
}  \note-mod "1" cis4  \note-mod "1" cis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "3" ees4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8[]
}  \note-mod "4" fis4  \note-mod "4" fis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. []
}  \note-mod "5" gis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4
~  \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "5" gis4  \note-mod "3" e4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[]
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
 \note-mod "4" fis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "7" b4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8[]
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "1" cis4^. ~  \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[
]   \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[]
}  \note-mod "7" b4  \note-mod "4" fis4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[
]   \note-mod "3" e4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8[]
}  \note-mod "5" gis4  \note-mod "5" gis4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]  ~  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "5" gis4^.  \note-mod "6" a4^.  \note-mod "6" a4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "6" a8[
]  ~  \note-mod "6" a4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "6" a8[]
}  \note-mod "6" a4  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)e4^.
 \note-mod "3" e4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8^.[
]   \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. []
}  \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "3" e4  \note-mod "4" fis4   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis8-\tweak #'X-offset #0.6 ^\two-dots [
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}  \note-mod "7" b4^.   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "5" gis4^.  \note-mod "5" gis4  \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
~ }  \note-mod "5" gis4  \note-mod "7" b4  \note-mod "4" fis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8[
]  ~  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4^.
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "7" b4  \note-mod "1" cis4 ~   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis8-\tweak #'X-offset #0.6 ^\two-dots [
]    \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
  \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis8-\tweak #'X-offset #0.6 ^\two-dots []
}  \note-mod "1" cis4^.  \note-mod "4" fis4^. ~  \note-mod "4" fis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" fis8^.[
]   \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[]
}  \note-mod "5" gis4  \note-mod "5" gis4^.  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[]
}  \note-mod "1" cis4  \note-mod "1" cis4  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "1" cis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8^.[]
}  \note-mod "1" cis4^.  \note-mod "1" cis4  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "7" b4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _. []
}  \note-mod "3" \once \tweak Accidental.extra-offset #'(0 . 0.7)ees4
~  \note-mod "3" ees4  \note-mod "7" b4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8^.[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "3" e4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "3" ees4^. ~  \note-mod "3" ees4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" ees8^.[
]   \note-mod "5" gis4^. ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8^.[]
}   \once \override Score.TextScript.outside-staff-priority = 45 \note-mod "1" cis4-\tweak #'X-offset #0.6 ^\two-dots 
 \note-mod "5" gis4  \note-mod "5" gis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" gis8[
]   \note-mod "1" cis4 ~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" cis8[]
~ }  \note-mod "1" cis4  \note-mod "1" cis4 \bar "|." } }
% === END JIANPU STAFF ===

>>
\header{
title="Music21 Fragment"
composer="Music21"
instrument=""
}
\layout{
  \context {
    \Global
    \grobdescriptions #all-grob-descriptions
  }
} }
\score {
\unfoldRepeats
<< 

% === BEGIN MIDI STAFF ===
    \new JianpuStaff { \new Voice="X" { \time 4/4 \tempo 4=80 b'''8 cis'4 ~ } cis'8 } cis'4 ~ gis'4 | %{ bar 2: %} gis'4 ~ } gis'8 e''4 ~ } e''8 } e''4 | %{ bar 3: %} gis'2 ~ } gis'8 e'''4 ~ } e'''8 } | %{ bar 4: %} gis''4 b'2 ~ } b'8 b''4 ~ } b''8 } b''4 cis''2 ~ } cis''8 gis'4 ~ } gis'8 } cis'4 gis'4 cis''4 ~ } cis''8 gis'4 ~ } gis'8 } gis''4 cis''4 fis''4 ~ } fis''8 cis''4 ~ } cis''8 } ees'''4 ees'''4 ees''4 ~ } ees''8 cis'''4 ~ } cis'''8 ~ } cis'''4 ees''2 ~ } ees''8 ees''4 ~ } ees''8 } b'4 gis''4 ees'''4 ~ } ees'''8 ~ ees'''4 ~ } ees'''8 } ees'''4 ees''4 b''4 ~ } b''8 cis'''4 ~ } cis'''8 } gis'4 gis'2 ~ } gis'8 e'4 ~ } e'8 } fis'4 gis'4 gis'4 ~ } gis'8 ~ gis'4 ~ } gis'8 } ees'4 ees''4 ees'4 ~ } ees'8 ees'4 ~ } ees'8 } ees'2 ees'4 ~ } ees'8 b4 ~ } b8 } ees''2 ees'4 ~ } ees'8 ees'4 ~ } ees'8 } gis'4 ees'2 ~ } ees'8 ees'4 ~ } ees'8 } fis'4 ees'4 ees''4 ~ } ees''8 ees'''4 ~ } ees'''8 } gis''4 ees'''4 ees''4 ~ } ees''8 ees''4 ~ } ees''8 } cis'''4 b''4 ees''4 ~ } ees''8 d'4 ~ } d'8 } ees'4 ees'2 ~ } ees'8 ees'4 ~ } ees'8 ~ } ees'4 fis'4 ees'4 ~ } ees'8 ees'4 ~ } ees'8 } gis'4 ees''4 gis'4 ~ } gis'8 ~ gis'4 ~ } gis'8 } e'4 b'4 cis''4 ~ } cis''8 gis'4 ~ } gis'8 ~ } gis'4 b4 gis'4 ~ } gis'8 gis'4 ~ } gis'8 ~ } gis'4 gis'4 gis'4 ~ } gis'8 b'4 ~ } b'8 } b'4 cis''4 fis'4 ~ } fis'8 b'4 ~ } b'8 } ees''4 cis''4 b'4 ~ } b'8 cis'''4 ~ } cis'''8 ~ } cis'''4 b4 fis'4 ~ } fis'8 b'4 ~ } b'8 } e'4 gis'4 gis'4 ~ } gis'8 gis'4 ~ } gis'8 } ees''4 gis'2 ~ } gis'8 a'4 ~ } a'8 } cis'4 e''4 e'4 ~ } e'8 b4 ~ } b8 } b4 gis'2 ~ } gis'8 b4 ~ } b8 } gis'4 e''4 fis''4 ~ } fis''8 gis'4 ~ } gis'8 } gis'4 ~ e'''4 gis'4 ~ } gis'8 ees''4 ~ } ees''8 } gis''2 gis''4 ~ } gis''8 gis''4 ~ } gis''8 } ees''4 ees''4 fis'4 ~ } fis'8 fis'4 ~ } fis'8 ~ } fis'4 b'4 cis''4 ~ } cis''8 cis''4 ~ } cis''8 } cis''4 a4 cis''4 ~ } cis''8 b4 ~ } b8 ~ } fis'4 fis'4 fis'4 ~ } fis'8 gis''4 ~ } gis''8 } gis''4 b4 gis'4 ~ } gis'8 e'4 ~ } e'8 } gis'4 fis'4 gis'4 ~ } gis'8 b'4 ~ } b'8 } gis'4 a'4 b'4 ~ } b'8 e''4 ~ } e''8 ~ } e''4 cis'4 e'4 ~ } e'8 e'4 ~ } e'8 } cis'''4 b4 cis'4 ~ } cis'8 gis'4 ~ } gis'8 } ees''4 ees''4 ees''4 ~ } ees''8 ees''4 ~ } ees''8 } b''4 ees''4 ees''4 ~ } ees''8 ~ ees''4 ~ } ees''8 } cis'4 gis'4 gis'4 ~ } gis'8 gis'4 ~ } gis'8 } cis'4 e''4 gis'4 ~ } gis'8 cis'4 ~ } cis'8 } e''4 e''4 gis'4 ~ } gis'8 e''4 ~ } e''8 } gis'4 cis'4 ees''4 ~ } ees''8 cis'4 ~ } cis'8 } ees''4 ees'4 ees'4 ~ } ees'8 a'4 ~ } a'8 } a'4 fis''4 ees''4 ~ } ees''8 a'4 ~ } a'8 } b4 fis'2 ~ } fis'8 b''4 ~ } b''8 } b'4 ees'''4 gis''4 ~ } gis''8 e''4 ~ } e''8 ~ } e''4 gis''4 e'''4 ~ } e'''8 gis''4 ~ } gis''8 } fis''4 ~ cis'4 e''4 ~ } e''8 ~ f''4 ~ } f''8 } ees''4 ees''4 ees''4 ~ } ees''8 cis''4 ~ } cis''8 } gis'4 gis''4 ees'4 ~ } ees'8 ~ ees'4 ~ } ees'8 } ees'4 gis''4 cis''4 ~ } cis''8 fis''4 ~ } fis''8 } e''4 fis''4 cis''4 ~ } cis''8 fis''4 ~ } fis''8 } cis'''4 e'4 fis'4 ~ } fis'8 e'4 ~ } e'8 } b''4 gis'4 ees'4 ~ } ees'8 gis'4 ~ } gis'8 ~ } gis'4 ees'4 gis4 ~ } gis8 ees''4 ~ } ees''8 } cis''4 ees'4 cis'4 ~ } cis'8 gis''4 ~ } gis''8 } gis''4 b'4 ees'4 ~ } ees'8 ees'4 ~ } ees'8 } b4 gis'4 d'4 ~ } d'8 e'4 ~ } e'8 } e'4 e'4 fis'4 ~ } fis'8 ~ fis'4 ~ } fis'8 } ees'4 fis'4 ees'4 ~ } ees'8 ees'4 ~ } ees'8 } b4 cis'2 ~ } cis'8 cis'4 ~ } cis'8 } e'4 gis'4 ees''4 ~ } ees''8 cis'4 ~ } cis'8 } cis'4 cis'2 ~ } cis'8 gis4 ~ } gis8 } gis'4 e'4 e'4 ~ } e'8 fis'4 ~ } fis'8 } fis'4 b'4 fis'4 ~ } fis'8 gis''4 ~ } gis''8 } gis''4 b4 fis'4 ~ } fis'8 fis'4 ~ } fis'8 } fis'4 gis''4 b'4 ~ } b'8 cis''4 ~ } cis''8 } cis''4 b'4 b'4 ~ } b'8 fis'4 ~ } fis'8 } b'4 gis'4 b'4 ~ } b'8 gis'4 ~ } gis'8 } fis'4 b'4 b'4 ~ } b'8 cis'4 ~ } cis'8 } cis''4 e'4 cis'4 ~ } cis'8 e'4 ~ } e'8 } cis'4 a'4 b4 ~ } b8 cis'4 ~ } cis'8 } ees'4 cis'4 ees''4 ~ } ees''8 cis'4 ~ } cis'8 } cis'4 cis''2 ~ } cis''8 ees''4 ~ } ees''8 } ees'4 fis'4 gis''4 ~ } gis''8 gis''4 ~ } gis''8 } gis'4 gis''2 ~ } gis''8 gis'4 ~ } gis'8 } gis'4 gis'4 fis'4 ~ } fis'8 fis'4 ~ } fis'8 } fis'2 gis''4 ~ } gis''8 gis''4 ~ } gis''8 } fis'4 b4 b'4 ~ } b'8 cis'''4 ~ } cis'''8 } b'4 b'4 fis'4 ~ } fis'8 gis4 ~ } gis8 ~ } gis4 gis'4 fis'4 ~ } fis'8 fis'4 ~ } fis'8 } gis'4 b'4 b'4 ~ } b'8 ~ b'4 ~ } b'8 } cis'4 e''4 cis'4 ~ } cis'8 cis'4 ~ } cis'8 ~ } cis'4 a'4 e'4 ~ } e'8 ees'4 ~ } ees'8 ~ } ees'4 a4 cis'4 ~ } cis'8 ees'4 ~ } ees'8 } gis4 gis'4 cis'4 ~ } cis'8 cis'4 ~ } cis'8 } cis'4 cis'4 ees''4 ~ } ees''8 ees'4 ~ } ees'8 } fis'4 fis'4 gis'4 ~ } gis'8 b4 ~ } b8 } gis'4 e'2 ~ } e'8 gis'4 ~ } gis'8 } gis'4 e'4 gis'4 ~ } gis'8 b'4 ~ } b'8 } ees'4 fis'4 gis'4 ~ } gis'8 b'4 ~ } b'8 } cis'''4 cis''2 ~ } cis''8 cis''4 ~ } cis''8 } b'4 fis'4 e'4 ~ } e'8 e'4 ~ } e'8 } gis'4 gis4 gis'4 ~ } gis'8 ~ gis'4 ~ } gis'8 } gis''4 a''4 a'4 ~ } a'8 ~ a'4 ~ } a'8 } a'4 e''4 e''4 ~ } e''8 b4 ~ } b8 } b4 b4 fis'4 ~ } fis'8 gis'4 ~ } gis'8 } e'4 fis'4 cis'''4 ~ } cis'''8 gis''4 ~ } gis''8 } b''4 cis'''4 fis'4 ~ } fis'8 gis'4 ~ } gis'8 } gis''4 gis'4 gis''4 ~ } gis''8 gis'4 ~ } gis'8 ~ } gis'4 b'4 fis'4 ~ } fis'8 ~ ees''4 ~ } ees''8 } b'4 cis'4 ~ cis'''4 ~ } cis'''8 cis'''4 ~ } cis'''8 } cis''4 fis''2 ~ } fis''8 gis'4 ~ } gis'8 } gis'4 gis''4 gis'4 ~ } gis'8 ees''4 ~ } ees''8 } cis'4 cis'4 ees''4 ~ } ees''8 cis''4 ~ } cis''8 } cis''4 cis'4 ees''4 ~ } ees''8 b4 ~ } b8 } ees'2 b''4 ~ } b''8 gis''4 ~ } gis''8 } e'''4 ees''2 ~ } ees''8 gis''4 ~ } gis''8 } cis'''4 gis'4 gis'4 ~ } gis'8 cis'4 ~ } cis'8 ~ } cis'4 cis'4 } }
% === END MIDI STAFF ===

>>
\header{
title="Music21 Fragment"
composer="Music21"
instrument=""
}
\midi { \context { \Score tempoWholesPerMinute = #(ly:make-moment 84 4)}} }
