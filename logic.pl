% ============================================================
%  logic.pl  —  Motor lógico del juego Tank-Attack
% ============================================================

% Hechos dinámicos cargados desde Python
:- dynamic muro/2.
:- dynamic objetivo/4.
:- dynamic tanque_enemigo/5.
:- dynamic jugador/2.
:- dynamic tablero_ancho/1.
:- dynamic tablero_alto/1.

% ============================================================
%  SECCIÓN 1 — HECHOS ESTÁTICOS
% ============================================================

% capacidad_tanque(Tipo, Velocidad, Rango, Resistencia)
% Rango está medido en celdas del mapa.
capacidad_tanque(ligero,        3, 6, 1).
capacidad_tanque(pesado,        1, 7, 4).
capacidad_tanque(francotirador, 2, 10, 2).

% resistencia_objetivo(Tipo, Vida)
resistencia_objetivo(radar,  2).
resistencia_objetivo(bunker, 4).

% ============================================================
%  SECCIÓN 2 — CELDAS BLOQUEADAS
% ============================================================

% Una celda está bloqueada si tiene muro o está fuera del tablero.
bloqueado(X, Y) :-
    muro(X, Y).

bloqueado(X, Y) :-
    tablero_ancho(W),
    tablero_alto(H),
    (
        X < 0 ;
        X >= W ;
        Y < 0 ;
        Y >= H
    ).

% ============================================================
%  SECCIÓN 3 — VECINOS VÁLIDOS
% ============================================================

% Movimiento en cuatro direcciones.
vecino(pos(X, Y), pos(NX, Y)) :-
    NX is X + 1,
    \+ bloqueado(NX, Y).

vecino(pos(X, Y), pos(NX, Y)) :-
    NX is X - 1,
    \+ bloqueado(NX, Y).

vecino(pos(X, Y), pos(X, NY)) :-
    NY is Y + 1,
    \+ bloqueado(X, NY).

vecino(pos(X, Y), pos(X, NY)) :-
    NY is Y - 1,
    \+ bloqueado(X, NY).

% ============================================================
%  SECCIÓN 4 — HEURÍSTICA
% ============================================================

% Distancia Manhattan.
heuristica(pos(X, Y), pos(GX, GY), Valor) :-
    Valor is abs(GX - X) + abs(GY - Y).

ordenar_vecinos(Vecinos, Meta, Ordenados) :-
    maplist(par_heuristica(Meta), Vecinos, Pares),
    msort(Pares, ParesOrdenados),
    pairs_values(ParesOrdenados, Ordenados).

par_heuristica(Meta, Vecino, H-Vecino) :-
    heuristica(Vecino, Meta, H).

% ============================================================
%  SECCIÓN 5 — DFS CON HEURÍSTICA
% ============================================================

camino_dfs(Inicio, Meta, Ruta) :-
    dfs(Inicio, Meta, [Inicio], RutaInvertida),
    reverse(RutaInvertida, Ruta).

dfs(Meta, Meta, Visitados, Visitados).

dfs(Actual, Meta, Visitados, Ruta) :-
    Actual \= Meta,
    findall(V, vecino(Actual, V), Vecinos),
    ordenar_vecinos(Vecinos, Meta, VecinosOrdenados),
    member(Siguiente, VecinosOrdenados),
    \+ member(Siguiente, Visitados),
    dfs(Siguiente, Meta, [Siguiente | Visitados], Ruta).

mejor_ruta(Inicio, Meta, Ruta) :-
    camino_dfs(Inicio, Meta, Ruta),
    !.

mejor_ruta(_, _, []).

% ============================================================
%  SECCIÓN 6 — DISTANCIA Y PROXIMIDAD
% ============================================================

distancia_manhattan(pos(X1, Y1), pos(X2, Y2), D) :-
    D is abs(X2 - X1) + abs(Y2 - Y1).

% Un tanque está cerca si el jugador está dentro del rango lógico.
cerca(IdTanque, pos(JX, JY)) :-
    tanque_enemigo(IdTanque, TX, TY, Tipo, _),
    capacidad_tanque(Tipo, _, Rango, _),
    distancia_manhattan(pos(TX, TY), pos(JX, JY), D),
    D =< Rango.

% ============================================================
%  SECCIÓN 7 — REGLAS DE DECISIÓN
% ============================================================

debe_atacar(IdTanque) :-
    jugador(JX, JY),
    cerca(IdTanque, pos(JX, JY)).

objetivo_mas_cercano(IdTanque, IdObj, pos(OX, OY)) :-
    tanque_enemigo(IdTanque, TX, TY, _, _),
    findall(
        D-Id-X-Y,
        (
            objetivo(Id, X, Y, _),
            distancia_manhattan(pos(TX, TY), pos(X, Y), D)
        ),
        Lista
    ),
    msort(Lista, [_-IdObj-OX-OY | _]).

debe_defender(IdTanque, IdObj) :-
    objetivo_mas_cercano(IdTanque, IdObj, pos(OX, OY)),
    jugador(JX, JY),
    tanque_enemigo(IdTanque, TX, TY, _, _),
    distancia_manhattan(pos(JX, JY), pos(OX, OY), DJ),
    distancia_manhattan(pos(TX, TY), pos(OX, OY), DT),
    DJ < DT.

% Ahora retroceder usa la vida real recibida desde Python.
debe_retroceder(IdTanque) :-
    tanque_enemigo(IdTanque, TX, TY, _, Vida),
    jugador(JX, JY),
    distancia_manhattan(pos(TX, TY), pos(JX, JY), D),
    Vida =< 40,
    D =< 8.

% ============================================================
%  SECCIÓN 8 — DECISIÓN FINAL
% ============================================================

decision(IdTanque, retroceder) :-
    debe_retroceder(IdTanque),
    !.

decision(IdTanque, atacar) :-
    debe_atacar(IdTanque),
    !.

decision(IdTanque, defender(IdObj)) :-
    debe_defender(IdTanque, IdObj),
    !.

decision(IdTanque, acercarse) :-
    tanque_enemigo(IdTanque, _, _, _, _),
    !.

decision(_, reposicionarse).

% ============================================================
%  SECCIÓN 9 — META SEGÚN ACCIÓN
% ============================================================

meta_segun_accion(_, atacar, pos(JX, JY)) :-
    jugador(JX, JY).

meta_segun_accion(_, defender(IdObj), pos(OX, OY)) :-
    objetivo(IdObj, OX, OY, _).

meta_segun_accion(_, acercarse, pos(JX, JY)) :-
    jugador(JX, JY).

meta_segun_accion(IdTanque, retroceder, pos(MX, MY)) :-
    tanque_enemigo(IdTanque, TX, TY, _, _),
    jugador(JX, JY),
    DX is TX - JX,
    DY is TY - JY,
    SX is sign(DX),
    SY is sign(DY),
    MX is TX + SX * 3,
    MY is TY + SY * 3.

meta_segun_accion(IdTanque, reposicionarse, pos(OX, OY)) :-
    objetivo_mas_cercano(IdTanque, _, pos(OX, OY)).

% ============================================================
%  SECCIÓN 10 — ACCIÓN Y RUTA
% ============================================================

accion_y_ruta(IdTanque, Accion, Ruta) :-
    decision(IdTanque, Accion),
    tanque_enemigo(IdTanque, TX, TY, _, _),
    meta_segun_accion(IdTanque, Accion, pos(MX, MY)),
    mejor_ruta(pos(TX, TY), pos(MX, MY), Ruta).

% ============================================================
%  SECCIÓN 11 — CARGA DINÁMICA DESDE PYTHON
% ============================================================

limpiar_nivel :-
    retractall(muro(_, _)),
    retractall(objetivo(_, _, _, _)),
    retractall(tanque_enemigo(_, _, _, _, _)),
    retractall(jugador(_, _)),
    retractall(tablero_ancho(_)),
    retractall(tablero_alto(_)).

cargar_tablero(W, H) :-
    assert(tablero_ancho(W)),
    assert(tablero_alto(H)).

agregar_muro(X, Y) :-
    assert(muro(X, Y)).

agregar_objetivo(Id, X, Y, Tipo) :-
    assert(objetivo(Id, X, Y, Tipo)).

agregar_tanque_enemigo(Id, X, Y, Tipo, Vida) :-
    assert(tanque_enemigo(Id, X, Y, Tipo, Vida)).

actualizar_jugador(X, Y) :-
    retractall(jugador(_, _)),
    assert(jugador(X, Y)).

actualizar_tanque(Id, NX, NY, Vida) :-
    tanque_enemigo(Id, _, _, Tipo, _),
    retractall(tanque_enemigo(Id, _, _, _, _)),
    assert(tanque_enemigo(Id, NX, NY, Tipo, Vida)).