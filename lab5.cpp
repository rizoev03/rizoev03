//Задание 1
program Begin1;
var x1, x2, y1, y2, d:real;
begin
readln(x1, y1);
readln(x2, y2);
d: = sqrt(sqr(x2 - x1) + sqr(y2 - y1));
writeln(d);
end.


//Задание 2

program Begin2;
var
A, B, C, AC, BC, Sum: Real;
begin
Write('Введите значение точки A: ');
Readln(A);
Write('Введите значение точки B: ');
Readln(B);
Write('Введите значение точки C: ');
Readln(C);
AC: = Abs(A - C);
Writeln('Расстояние отрезка AC равно: ', AC);
BC: = Abs(B - C);
Writeln('Расстояние отрезка BC равно: ', BC);
Sum: = AC + BC;
Writeln('Сумма отрезков AC и BC равно: ', Sum);
end.


//Задание 3

program Begin3;
var
A, B, C, AC, BC, product: Real;
begin
Write('Введите значение точки A: ');
Readln(A);
Write('Введите значение точки B: ');
Readln(B);
Write('Введите значение точки C: ');
Readln(C);
AC: = Abs(A - C);
Writeln('Расстояние отрезка AC равно: ', AC);
BC: = Abs(C - B);
Writeln('Расстояние отрезка BC равно: ', BC);
product: = AC * BC;
Writeln('Произведение отрезков AC и BC равно: ', product);
end.


//Задание 4

program Begin4;
var
x1, y1, x2, y2, P, S: Real;
begin
Writeln('Введите значение координат певой точки прямоугольника: ');
Write('Введите значение x: ');
Readln(x1);
Write('Введите значение y: ');
Readln(y1);
Writeln('Введите значение координат второй точки прямоугольника: ');
Write('Введите значение x: ');
Readln(x2);
Write('Введите значение y: ');
Readln(y2);
P: = 2 * (abs(x1 - x2) + abs(y1 - y2));
Writeln('Периметр прямоугольника равен: ', P);
S: = abs(x1 - x2) * abs(y1 - y2);
Writeln('Площадь прямоугольника равна: ', S);
end.

//Задание 5

program z_8;
var x1, y1, x2, y2, x3, y3, P, p2, S, a, b, c: real;
begin
write('Координаты первой точки (через пробел)');  read(x1, y1);
write('Координаты второй точки (через пробел)');  read(x2, y2);
write('Координаты третьей точки (через пробел)');  read(x3, y3);
a: = sqrt(sqr(x2 - x1) + sqr(y2 - y1));
b: = sqrt(sqr(x3 - x2) + sqr(y3 - y2));
c: = sqrt(sqr(x3 - x1) + sqr(y3 - y1));
P: = a + b + c;
p2: = P / 2;
S: = sqrt(p2 * (p2 - a) * (p2 - b) * (p2 - c));
writeln('Периметр: ', P);
writeln('Площадь: ', S);
end.
