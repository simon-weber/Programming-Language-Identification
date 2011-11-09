#Copyright (c) 2011 David Klein and Simon Weber
#Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

echo "Which directory do you want to process: "
read direct

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
echo "Actionscript..."
for f in $(find $direct -iname '*.as')
do
	`python reader.py -l actionscript < $f`
done

echo "Ada..."
for f in $(find $direct -iname '*.ads')
do
	`python reader.py -l ada < $f`
done

echo "Brainfuck..."
for f in $(find $direct -iname '*.b')
do
	`python reader.py -l brainfuck < $f`
done

echo "C..."
for f in $(find $direct -iname '*.c')
do
	`python reader.py -l c < $f`
done

echo "C++..."
for f in $(find $direct -iname '*.cpp')
do
	`python reader.py -l cplusplus < $f`
done

echo "C#..."
for f in $(find $direct -iname '*.cs')
do
	`python reader.py -l csharp < $f`
done

echo "CSS..."
for f in $(find $direct -iname '*.css')
do
	`python reader.py -l css < $f`
done

echo "Erlang..."
for f in $(find $direct -iname '*.erl')
do
	`python reader.py -l erlang < $f`
done

echo "Haskell..."
for f in $(find $direct -iname '*.hs')
do
	`python reader.py -l haskell < $f`
done

echo "HTML..."
for f in $(find $direct -iname '*.htm*')
do
	`python reader.py -l html < $f`
done

echo "Java..."
for f in $(find $direct -iname '*.java')
do
	`python reader.py -l java < $f`
done

echo "Javascript..."
for f in $(find $direct -iname '*.js')
do
	`python reader.py -l javascript < $f`
done

echo "Latex..."
for f in $(find $direct -iname '*.tex')
do
	`python reader.py -l latex < $f`
done

echo "Lisp..."
for f in $(find $direct -iname '*.lisp')
do
	`python reader.py -l lisp < $f`
done

echo "Lua..."
for f in $(find $direct -iname '*.lua')
do
	`python reader.py -l lua < $f`
done

echo "Matlab..."
for f in $(find $direct -iname '*.matlab')
do
	`python reader.py -l matlab < $f`
done

echo "Objective C..."
for f in $(find $direct -iname '*.m')
do
	`python reader.py -l objectivec < $f`
done

echo "PHP..."
for f in $(find $direct -iname '*.php')
do
	`python reader.py -l php < $f`
done

echo "Python..."
for f in $(find $direct -iname '*.py')
do
	`python reader.py -l python < $f`
done

echo "Ruby..."
for f in $(find $direct -iname '*.rb')
do
	`python reader.py -l ruby < $f`
done

echo "Scala..."
for f in $(find $direct -iname '*.scala')
do
	`python reader.py -l scala < $f`
done

echo "Scheme..."
for f in $(find $direct -iname '*.scm')
do
	`python reader.py -l scheme < $f`
done

echo "Smalltalk..."
for f in $(find $direct -iname '*.st')
do
	`python reader.py -l smalltalk < $f`
done

echo "XML..."
for f in $(find $direct -iname '*.xml')
do
	`python reader.py -l xml < $f`
done
IFS=$SAVEIFS
