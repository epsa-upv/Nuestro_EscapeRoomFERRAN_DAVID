/* EscapeHub — capa de presentación. Sin arrays falsos ni acceso directo a SQL.
 * Requiere la API de doc/api_rest.md implementada por David.
 */
(function () {
  'use strict';
  const api = window.EscapeAPI;
  const $ = id => document.getElementById(id);
  const state = { user: null, rooms: [], sessions: [], reservations: [], results: [], games: [], activeGame: null, adminChallenges: [], adminObjects: [], requestId: 0, gameRequest: 0 };

  function text(tag, content, className = '') {
    const el = document.createElement(tag);
    el.textContent = content ?? '';
    if (className) el.className = className;
    return el;
  }
  function clear(el) { el.replaceChildren(); }
  function empty(el, message) { clear(el); el.append(text('p', message, 'empty')); }
  function message(value, type = '') {
    const n = $('notice');
    n.textContent = value;
    n.className = `notice${type ? ' ' + type : ''}`;
    n.hidden = !value;
  }
  function report(error) {
    console.error(error);
    message(error?.message || 'Ha ocurrido un error inesperado.', 'error');
    if (error?.status === 401 && state.user) signOut(true);
  }
  async function busy(form, fn) {
    const button = form.querySelector('[type="submit"]');
    if (button?.disabled) return;
    if (button) button.disabled = true;
    try { await fn(); } catch (error) { report(error); }
    finally { if (button) button.disabled = false; }
  }
  function isAdmin() { return state.user?.rol === 'ADMIN'; }
  function isPlayer() { return state.user?.rol === 'JUGADOR'; }
  function positiveInt(value) { return Number.isSafeInteger(Number(value)) && Number(value) > 0 ? Number(value) : null; }
  function toList(data, label) {
    if (!Array.isArray(data)) throw new Error(`Formato de respuesta no válido: ${label} debe ser una lista JSON.`);
    return data;
  }
  function readableDate(s) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(s || ''))) return String(s || '');
    const [y,m,d] = s.split('-');
    return `${d}/${m}/${y}`;
  }
  function showPanels() {
    $('auth-section').hidden = !!state.user;
    $('player-section').hidden = !isPlayer();
    $('admin-section').hidden = !isAdmin();
    $('game-section').hidden = !isPlayer();
    $('logout').hidden = !state.user;
    $('whoami').hidden = !state.user;
    $('whoami').textContent = state.user ? `${state.user.nombre} · ${state.user.rol}` : '';
  }
  function signOut(expired = false) {
    api.clearToken(); state.user = null; state.reservations = []; state.results = []; state.games = []; state.activeGame = null;
    showPanels();
    renderGameReservations();
    $('login-password').value = '';
    if (expired) message('Tu sesión ha caducado. Vuelve a iniciar sesión.', 'error');
    else message('Sesión cerrada correctamente.', 'success');
  }
  function glyph(theme) {
    const t = String(theme || '').toLowerCase();
    if (t.includes('terror')) return '♜';
    if (t.includes('ciencia')) return '✧';
    if (t.includes('mister') || t.includes('invest')) return '⌕';
    if (t.includes('avent')) return '⚑';
    return '⌘';
  }
  function fillSelect(id, items, placeholder, labelFn) {
    const sel = $(id), selected = sel.value;
    clear(sel);
    const first = document.createElement('option');
    first.value = ''; first.textContent = placeholder;
    sel.append(first);
    items.forEach(item => {
      const opt = document.createElement('option');
      opt.value = String(item.id);
      opt.textContent = labelFn(item);
      sel.append(opt);
    });
    if ([...sel.options].some(o => o.value === selected)) sel.value = selected;
  }
  function renderRooms() {
    const container = $('rooms'); clear(container);
    if (!state.rooms.length) empty(container, 'Todavía no hay salas registradas. Crea primero una sala como administrador.');
    state.rooms.forEach(room => {
      const article = document.createElement('article'); article.className = 'room-card';
      const top = text('div', '', 'room-top');
      top.append(text('span', glyph(room.tematica), 'room-glyph'));
      const pill = text('span', room.activa ? 'DISPONIBLE' : 'INACTIVA', `room-state${room.activa ? '' : ' off'}`);
      top.append(pill);
      const body = text('div', '', 'room-body');
      body.append(text('div', room.tematica, 'room-theme'), text('div', room.nombre, 'room-title'));
      const facts = text('div', '', 'room-facts');
      facts.append(text('span', `◷ ${room.duracion_minutos} min`), text('span', `♙ ${room.capacidad} jugadores`), text('span', `✦ ${room.dificultad}`));
      body.append(facts); article.append(top, body); container.append(article);
    });
    const active = state.rooms.filter(r => r.activa);
    fillSelect('booking-room', active, 'Selecciona una sala', r => `${r.nombre} · máximo ${r.capacidad}`);
    fillSelect('session-room', active, 'Selecciona una sala', r => r.nombre);
    fillSelect('challenge-room', state.rooms, 'Selecciona sala', r => r.nombre);
    fillSelect('object-room', state.rooms, 'Selecciona sala', r => r.nombre);
    if (isAdmin() && state.rooms.length && !$('challenge-room').value) {
      $('challenge-room').value = String(state.rooms[0].id);
      loadAdminChallenges().catch(report);
    }
    renderAdminRooms();
  }
  async function loadRooms() { state.rooms = toList(await api.rooms(), 'salas'); renderRooms(); }
  async function loadSessions() {
    const requestId = ++state.requestId;
    const roomId = $('booking-room').value;
    const slot = $('booking-session');
    if (!roomId) { fillSelect('booking-session', [], 'Selecciona primero una sala', x => x); return; }
    const params = { sala_id: roomId, estado: 'DISPONIBLE' };
    const fecha = $('booking-date').value;
    if (!fecha) {
      state.sessions = [];
      fillSelect('booking-session', [], 'Selecciona primero una fecha', x => x);
      return;
    }
    params.fecha = fecha;
    clear(slot); slot.append(new Option('Cargando sesiones…', ''));
    try {
      const sessions = toList(await api.sessions(params), 'sesiones');
      if (requestId !== state.requestId) return;
      state.sessions = sessions.filter(s => String(s.sala_id) === String(roomId) && s.estado === 'DISPONIBLE' && s.fecha === fecha);
      fillSelect('booking-session', state.sessions, 'Selecciona una sesión', s => `${readableDate(s.fecha)} · ${String(s.hora_inicio).slice(0, 5)}`);
      if (!state.sessions.length) message('No hay sesiones disponibles para los filtros indicados.', '');
    } catch (error) {
      if (requestId === state.requestId) fillSelect('booking-session', [], 'No se pudieron cargar sesiones', x => x);
      report(error);
    }
  }
  function createAction(label, className, onClick) {
    const button = text('button', label, `btn ${className}`);
    button.type = 'button';
    button.addEventListener('click', async () => {
      button.disabled = true;
      try { await onClick(); } catch (error) { report(error); }
      finally { button.disabled = false; }
    });
    return button;
  }
  function record(parent, title, metadata, badge, actions = []) {
    const item = text('div', '', 'record'), left = text('div', '', ''), heading = text('div', title, 'record-title');
    if (badge) heading.append(text('span', badge, `status-pill${badge === 'CANCELADA' ? ' cancelled' : ''}`));
    left.append(heading, text('div', metadata, 'record-meta')); item.append(left);
    if (actions.length) { const right = text('div', '', 'record-actions'); actions.forEach(a => right.append(a)); item.append(right); }
    parent.append(item);
  }
  function renderGameReservations() {
    const list = state.reservations.filter(r => r.estado === 'ACTIVA');
    const select = $('game-reservation');
    const selected = select.value;
    select.replaceChildren(new Option(list.length ? 'Selecciona una reserva' : 'No tienes reservas activas', ''));
    list.forEach(r => {
      const sesion = r.sesion || {};
      const nombre = sesion.sala?.nombre || `Sala de la sesión #${r.sesion_id}`;
      select.add(new Option(`${nombre} · ${readableDate(sesion.fecha)} ${String(sesion.hora_inicio || '').slice(0,5)} · reserva #${r.id}`, String(r.id)));
    });
    if (list.some(r => String(r.id) === selected)) select.value = selected;
    select.disabled = !list.length;
    $('create-game-form').querySelector('[type="submit"]').disabled = !list.length;
    $('game-help').textContent = !list.length
      ? 'No tienes reservas activas. Primero reserva una sesión desde el panel de jugador. La sesión debe ser futura.'
      : 'Crear partida no significa iniciarla. El botón «Iniciar partida» solo funciona desde 15 minutos antes del horario reservado hasta su finalización prevista, y la sala debe tener retos activos.';
  }

  async function createOrOpenGame(reservationId) {
    if (!isPlayer()) throw new Error('Para crear partidas debes iniciar sesión con una cuenta JUGADOR; los ADMIN solo configuran las salas.');
    const existing = state.games.find(g => Number(g.reserva_id) === reservationId);
    if (existing) {
      await openGame(existing.id);
      message(`Partida #${existing.id} abierta.`, 'success');
      $('game-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    const game = await api.createGame(reservationId);
    await loadGames();
    if (game?.id) await openGame(game.id);
    message('Partida creada. Para iniciarla, comprueba el horario y que la sala tenga retos activos.', 'success');
    $('game-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  async function loadReservations() {
    state.reservations = toList(await api.reservations(), 'reservas');
    renderGameReservations();
    const area = $('reservations'); clear(area);
    if (!state.reservations.length) return empty(area, 'Todavía no tienes reservas.');
    state.reservations.forEach(r => {
      const s = r.sesion || {}, room = s.sala || {};
      const actions = [];
      if (r.estado === 'ACTIVA') {
        actions.push(createAction('Crear/abrir partida', 'btn-outline', async () => {
          await createOrOpenGame(Number(r.id));
        }));
        actions.push(createAction('Cancelar', 'btn-danger', async () => {
          if (!window.confirm('¿Cancelar esta reserva? Se aplicará la regla de 24 horas.')) return;
          await api.cancel(r.id); message('Reserva cancelada.', 'success');
          await Promise.all([loadReservations(), loadSessions()]);
        }));
      }
      record(area, room.nombre || `Sesión #${r.sesion_id}`, `${readableDate(s.fecha)} · ${String(s.hora_inicio || '').slice(0,5)} · ${r.numero_jugadores} jugadores`, r.estado, actions);
    });
  }
  function startEdit(room) {
    $('room-form').dataset.editId = String(room.id);
    $('room-name').value = room.nombre;
    $('room-theme').value = room.tematica;
    $('room-difficulty').value = room.dificultad;
    $('room-duration').value = room.duracion_minutos;
    $('room-capacity').value = room.capacidad;
    $('room-form').querySelector('[type="submit"]').textContent = 'Guardar cambios →';
    $('room-name').focus();
    message(`Editando la sala «${room.nombre}». Guarda los cambios o recarga la página para salir de edición.`);
  }
  function resetRoomForm() {
    $('room-form').reset();
    delete $('room-form').dataset.editId;
    $('room-form').querySelector('[type="submit"]').textContent = 'Crear sala →';
  }
  function renderAdminRooms() {
    const area = $('admin-rooms'); clear(area);
    if (!state.rooms.length) return empty(area, 'No hay salas registradas.');
    state.rooms.forEach(room => {
      record(area, room.nombre, `${room.tematica} · ${room.capacidad} plazas · ${room.dificultad}`, room.activa ? '' : 'INACTIVA', [
        createAction('Editar', 'btn-outline', async () => startEdit(room)),
        createAction('Eliminar', 'btn-danger', async () => {
          if (!window.confirm(`¿Eliminar «${room.nombre}»? No se permite si tiene sesiones vinculadas.`)) return;
          await api.deleteRoom(room.id); message('Sala eliminada.', 'success');
          await loadRooms();
        })
      ]);
    });
  }
  async function loadResults() {
    state.results = toList(await api.results(), 'resultados');
    const area = $('results'); clear(area);
    if (!state.results.length) return empty(area, 'Aún no se han registrado resultados.');
    state.results.forEach(r => record(area, r.nombre_equipo, `Sesión #${r.sesion_id} · ${r.tiempo_minutos == null ? 'Sin tiempo registrado' : r.tiempo_minutos + ' min'}`, r.superada ? 'SUPERADA' : 'NO SUPERADA'));
  }
  function safeLabel(value) { return String(value ?? '').slice(0, 400); }

  async function loadGames() {
    const area = $('games-list');
    let games;
    try { games = toList(await api.games(), 'partidas'); }
    catch (err) { empty(area, `No se pudieron cargar las partidas: ${err.message}`); throw err; }
    state.games = games;
    clear(area);
    if (!state.games.length) return empty(area, 'Todavía no hay partidas. Crea una desde una reserva activa.');
    state.games.forEach(game => {
      record(area, `Partida #${game.id}`, `Reserva #${game.reserva_id} · ${game.sala?.nombre || 'Sala #' + game.sala_id}`, game.estado,
        [createAction('Abrir', 'btn-outline', () => openGame(game.id))]);
    });
  }

  async function openGame(id) {
    const currentRequest = ++state.gameRequest;
    const game = await api.game(id);
    if (currentRequest !== state.gameRequest || !isPlayer()) return;
    state.activeGame = game;
    renderGame();
  }

  function renderGame() {
    const game = state.activeGame;
    if (!game) return;
    $('game-title').textContent = `Partida #${game.id}`;
    const retos = Array.isArray(game.retos) ? game.retos : [];
    const completed = retos.filter(r => r.estado === 'COMPLETADO').length;
    $('game-summary').textContent = `Estado: ${game.estado} · Retos completados: ${completed}/${retos.length}`;
    const actions = $('game-actions'); clear(actions);
    if (game.estado === 'PENDIENTE') {
      actions.append(text('p', 'Puedes iniciar esta partida desde 15 minutos antes de la sesión, hasta su hora de fin prevista. La sala necesita al menos un reto activo.', 'muted'));
      actions.append(createAction('Iniciar partida', 'btn-primary', async () => {
        await api.startGame(game.id);
        await Promise.all([loadGames(), openGame(game.id)]);
        message('Partida iniciada. ¡Resuelve los retos!', 'success');
      }));
    } else if (game.estado === 'EN_CURSO') {
      actions.append(text('p', 'Partida en curso. El progreso se consulta y guarda en PostgreSQL.', 'muted'));
    } else {
      actions.append(text('p', 'Esta partida ha terminado y solo se puede consultar su resultado.', 'muted'));
    }
    const area = $('game-challenges'); clear(area);
    if (!retos.length) empty(area, 'No hay retos configurados para esta partida.');
    retos.sort((a,b) => Number(a.orden)-Number(b.orden)).forEach(reto => {
      const card = text('article', '', 'challenge-item');
      card.append(text('h4', `${reto.orden}. ${safeLabel(reto.titulo)}`), text('p', safeLabel(reto.descripcion), 'muted'));
      const badge = text('span', reto.estado, 'status-pill'); card.append(badge);
      if (reto.estado === 'DISPONIBLE' && game.estado === 'EN_CURSO') {
        if (reto.tipo === 'OBJETO') {
          const availableObjects = Array.isArray(game.inventario) ? game.inventario.filter(o => !o.consumido) : [];
          if (!availableObjects.length) card.append(text('p', 'Necesitas encontrar un objeto para resolver este reto.', 'muted'));
          else {
            const form = document.createElement('form'); form.className='form-stack spaced-top';
            const label = text('label', 'Selecciona el objeto a utilizar');
            const sel = document.createElement('select');
            availableObjects.forEach(obj => { const opt = new Option(obj.nombre, String(obj.id)); sel.append(opt); });
            label.append(sel); const btn = text('button','Usar objeto','btn btn-outline'); btn.type='submit'; form.append(label,btn);
            form.addEventListener('submit', e => { e.preventDefault(); busy(form, async () => {
              const objectId = positiveInt(sel.value); if (!objectId) throw new Error('Selecciona un objeto.');
              const result = await api.useObject(game.id, reto.id, objectId);
              message(result.correcta ? '¡Objeto correcto! Reto completado.' : 'Ese objeto no resuelve el reto.', result.correcta ? 'success' : '');
              await Promise.all([loadGames(), openGame(game.id)]);
            }); }); card.append(form);
          }
        } else if (reto.tipo === 'OPCION') {
          const options = Array.isArray(reto.opciones) ? reto.opciones : [];
          if (options.length < 2) card.append(text('p', 'Este reto no tiene opciones configuradas. Consulta con el administrador.', 'muted'));
          else {
            const choices = text('div', '', 'challenge-options-list');
            choices.append(text('p', 'Selecciona la respuesta:', 'muted'));
            options.forEach(option => {
              if (typeof option !== 'string') return;
              choices.append(createAction(option, 'btn-outline challenge-choice', async () => {
                const buttons = [...choices.querySelectorAll('button')];
                buttons.forEach(b => { b.disabled = true; });
                try {
                  const result = await api.submitAnswer(game.id, reto.id, option);
                  message(result.correcta ? '¡Correcto! Progreso guardado.' : 'Respuesta incorrecta.', result.correcta ? 'success' : '');
                  await Promise.all([loadGames(), openGame(game.id)]);
                } finally { buttons.forEach(b => { b.disabled = false; }); }
              }));
            });
            card.append(choices);
          }
        } else {
          const form = document.createElement('form'); form.className = 'form-stack spaced-top';
          const label = text('label', 'Introduce tu respuesta');
          const input = document.createElement('input'); input.required = true; input.autocomplete = 'off'; input.maxLength = 500;
          label.append(input);
          const submit = text('button', 'Comprobar respuesta', 'btn btn-outline'); submit.type='submit';
          form.append(label, submit);
          form.addEventListener('submit', e => { e.preventDefault(); busy(form, async () => {
            const answer = input.value.trim(); if (!answer) throw new Error('Introduce una respuesta.');
            const result = await api.submitAnswer(game.id, reto.id, answer);
            input.value = '';
            message(result.correcta ? '¡Correcto! Progreso guardado.' : 'Respuesta incorrecta. Inténtalo de nuevo.', result.correcta ? 'success' : '');
            await Promise.all([loadGames(),openGame(game.id)]);
          }); }); card.append(form);
        }
        const hints = Array.isArray(reto.pistas) ? reto.pistas : [];
        hints.forEach(hint => {
          const box = text('div', '', 'hint-row');
          const button = createAction(`Solicitar pista ${hint.orden} (${hint.penalizacion_segundos || 0}s)`, 'btn-ghost', async () => {
            if (!window.confirm('¿Usar esta pista? Puede aplicar una penalización de tiempo.')) return;
            const result = await api.useHint(game.id, reto.id, hint.id);
            message(`Pista: ${safeLabel(result.contenido)}`, 'success');
            await openGame(game.id);
          });
          if (hint.usada) button.disabled = true;
          box.append(button);
          if (hint.usada && hint.contenido) box.append(text('p', safeLabel(hint.contenido), 'muted'));
          card.append(box);
        });
      }
      area.append(card);
    });
    const inv = $('game-inventory'); clear(inv); inv.append(text('h3', 'Inventario'));
    const inventory = Array.isArray(game.inventario) ? game.inventario : [];
    if (!inventory.length) inv.append(text('p', 'Todavía no hay objetos recogidos.', 'muted'));
    inventory.forEach(obj => record(inv, safeLabel(obj.nombre), obj.consumido ? 'Consumido' : 'Disponible', ''));
    const objects = Array.isArray(game.objetos_disponibles) ? game.objetos_disponibles : [];
    if (game.estado === 'EN_CURSO') objects.forEach(obj => {
      inv.append(createAction(`Recoger ${safeLabel(obj.nombre)}`, 'btn-outline', async () => {
        await api.collectObject(game.id, obj.id); message('Objeto añadido al inventario.', 'success'); await openGame(game.id);
      }));
    });
  }

  function normalizeOption(value) {
    return String(value).trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, ' ');
  }
  function parseOptions() {
    return $('challenge-options').value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  }
  function refreshChallengeType() {
    const type = $('challenge-type').value;
    $('challenge-answer-wrapper').hidden = type === 'OBJETO';
    $('challenge-options-wrapper').hidden = type !== 'OPCION';
    $('challenge-required-object-wrapper').hidden = type !== 'OBJETO';
    $('challenge-answer').disabled = type === 'OBJETO';
    $('challenge-answer').required = type !== 'OBJETO' && !$('challenge-form').dataset.editId;
  }
  function resetChallengeForm() {
    $('challenge-form').reset();
    delete $('challenge-form').dataset.editId;
    delete $('challenge-form').dataset.originalOptions;
    $('challenge-form').querySelector('[type="submit"]').textContent = 'Crear reto';
    refreshChallengeType();
  }
  async function loadChallengeObjects() {
    const roomId = $('challenge-room').value;
    state.adminObjects = [];
    fillSelect('challenge-required-object', [], 'Selecciona objeto', o => o.nombre);
    if (!roomId) return;
    const objects = toList(await api.objects(roomId), 'objetos');
    if ($('challenge-room').value !== roomId) return;
    state.adminObjects = objects;
    fillSelect('challenge-required-object', objects, 'Selecciona objeto', o => o.nombre);
  }
  async function loadObjectUnlockChallenges() {
    const roomId = $('object-room').value;
    fillSelect('object-unlock-challenge', [], 'Disponible desde el inicio', r => r.titulo);
    if (!roomId) return;
    const challenges = toList(await api.challenges(roomId), 'retos');
    if ($('object-room').value !== roomId) return;
    fillSelect('object-unlock-challenge', challenges, 'Disponible desde el inicio', r => `${r.orden}. ${r.titulo}`);
  }

  async function loadAdminChallenges() {
    const roomId = $('challenge-room').value;
    const area = $('admin-challenges'); clear(area);
    if (!roomId) { state.adminChallenges = []; fillChallengeSelectors(); return empty(area, 'Selecciona una sala para mostrar sus retos.'); }
    const data = toList(await api.challenges(roomId), 'retos');
    if ($('challenge-room').value !== roomId) return;
    state.adminChallenges = data;
    fillChallengeSelectors();
    await loadChallengeObjects();
    if (!data.length) return empty(area, 'Esta sala todavía no tiene retos.');
    data.forEach(r => record(area, `${r.orden}. ${r.titulo}`, `${r.tipo} · ${safeLabel(r.descripcion)}`, r.activo === false ? 'INACTIVO' : '', [
      createAction('Editar', 'btn-outline', async () => {
        $('challenge-form').dataset.editId = String(r.id);
        $('challenge-title').value = r.titulo;
        $('challenge-description').value = r.descripcion;
        $('challenge-type').value = r.tipo;
        $('challenge-order').value = r.orden;
        $('challenge-answer').value = '';
        $('challenge-options').value = Array.isArray(r.opciones) ? r.opciones.join('\n') : '';
        $('challenge-form').dataset.originalOptions = JSON.stringify(Array.isArray(r.opciones) ? r.opciones : []);
        $('challenge-required-object').value = r.objeto_requerido_id == null ? '' : String(r.objeto_requerido_id);
        refreshChallengeType();
        $('challenge-form').querySelector('[type="submit"]').textContent = 'Guardar cambios';
        $('challenge-title').focus();
        message('Edición de reto: deja solución vacía para conservar el hash anterior.');
      }),
      createAction('Eliminar', 'btn-danger', async () => {
        if (!window.confirm(`¿Eliminar el reto «${r.titulo}»?`)) return;
        await api.deleteChallenge(r.id); message('Reto eliminado.', 'success'); await loadAdminChallenges();
      })
    ]));
  }
  function fillChallengeSelectors() {
    ['hint-challenge', 'dependency-challenge', 'dependency-prerequisite'].forEach(id =>
      fillSelect(id, state.adminChallenges, 'Selecciona reto', r => `${r.orden}. ${r.titulo}`));
  }

  function hookupGameForms() {
    $('challenge-form').addEventListener('submit', e => {
      e.preventDefault(); busy(e.currentTarget, async () => {
        const sala_id = positiveInt($('challenge-room').value);
        const orden = positiveInt($('challenge-order').value);
        const tipo = $('challenge-type').value;
        const titulo = $('challenge-title').value.trim();
        const descripcion = $('challenge-description').value.trim();
        const respuesta = $('challenge-answer').value.trim();
        const editId = $('challenge-form').dataset.editId;
        if (!sala_id || !orden || !titulo || !descripcion) throw new Error('Completa los campos obligatorios del reto.');
        const body = { titulo, descripcion, tipo, orden, activo: true };
        if (tipo === 'OBJETO') {
          const id = positiveInt($('challenge-required-object').value);
          if (!id) throw new Error('Selecciona el objeto que resuelve el reto. Créalo primero si no existe.');
          body.objeto_requerido_id = id;
        } else if (tipo === 'OPCION') {
          const opciones = parseOptions();
          if (opciones.length < 2) throw new Error('Escribe al menos dos opciones, una por línea.');
          if (opciones.some(o => o.length > 200)) throw new Error('Cada opción admite un máximo de 200 caracteres.');
          const normalized = opciones.map(normalizeOption);
          if (new Set(normalized).size !== opciones.length) throw new Error('No repitas opciones.');
          const oldOptions = JSON.parse($('challenge-form').dataset.originalOptions || '[]');
          if (!editId || JSON.stringify(oldOptions) !== JSON.stringify(opciones)) {
            body.opciones = opciones;
            if (!respuesta) throw new Error('Escribe la solución correcta al crear o modificar opciones.');
          }
          if (respuesta && !normalized.includes(normalizeOption(respuesta))) throw new Error('La solución debe ser una de las opciones.');
          if (respuesta) body.respuesta = respuesta;
        } else {
          if (!editId && !respuesta) throw new Error('Escribe la solución del reto.');
          if (respuesta) body.respuesta = respuesta;
        }
        if (editId) await api.updateChallenge(editId, body);
        else await api.addChallenge(sala_id, body);
        resetChallengeForm();
        message(editId ? 'Reto actualizado.' : 'Reto creado mediante la API.', 'success');
        await loadAdminChallenges();
        if ($('object-room').value === String(sala_id)) await loadObjectUnlockChallenges();
      });
    });
    $('hint-form').addEventListener('submit', e => {
      e.preventDefault(); busy(e.currentTarget, async () => {
        const id = positiveInt($('hint-challenge').value), orden = positiveInt($('hint-order').value);
        const contenido = $('hint-content').value.trim(), penalizacion_segundos = Number($('hint-penalty').value);
        if (!id || !orden || !contenido || !Number.isSafeInteger(penalizacion_segundos) || penalizacion_segundos < 0) throw new Error('Revisa los datos de la pista.');
        await api.addHint(id, { orden, contenido, penalizacion_segundos });
        $('hint-content').value=''; $('hint-order').value='';
        message('Pista creada.', 'success');
      });
    });
    $('object-form').addEventListener('submit', e => {
      e.preventDefault(); busy(e.currentTarget, async () => {
        const id = positiveInt($('object-room').value), nombre=$('object-name').value.trim(), descripcion=$('object-description').value.trim();
        if (!id || !nombre) throw new Error('Selecciona sala y nombre de objeto.');
        const body = { nombre, descripcion, activo: true };
        const unlock = positiveInt($('object-unlock-challenge').value);
        if (unlock) body.reto_desbloqueo_id = unlock;
        await api.addObject(id, body);
        $('object-name').value = ''; $('object-description').value = '';
        if (String(id) === $('challenge-room').value) await loadChallengeObjects();
        message('Objeto creado.', 'success');
      });
    });
    $('dependency-form').addEventListener('submit', e => {
      e.preventDefault(); busy(e.currentTarget, async () => {
        const reto = positiveInt($('dependency-challenge').value), prerequisito_id = positiveInt($('dependency-prerequisite').value);
        if (!reto || !prerequisito_id || reto === prerequisito_id) throw new Error('Elige dos retos distintos de la misma sala.');
        await api.addDependency(reto, { prerequisito_id }); message('Dependencia creada.', 'success');
      });
    });
  }

  function hookup() {
    $('logout').addEventListener('click', () => signOut());
    $('refresh-rooms').addEventListener('click', () => loadRooms().catch(report));
    $('refresh-challenge-rooms').addEventListener('click', () => loadRooms().catch(report));
    $('booking-room').addEventListener('change', () => loadSessions());
    $('booking-date').addEventListener('change', () => loadSessions());
    $('refresh-reservations').addEventListener('click', () => loadReservations().catch(report));
    $('refresh-results').addEventListener('click', () => loadResults().catch(report));
    $('refresh-games').addEventListener('click', () => loadGames().catch(report));
    $('refresh-game-data').addEventListener('click', () => Promise.all([loadGames(), loadReservations()]).catch(report));
    $('create-game-form').addEventListener('submit', e => {
      e.preventDefault();
      busy(e.currentTarget, async () => {
        const reservationId = positiveInt($('game-reservation').value);
        if (!reservationId) throw new Error('Primero tienes que seleccionar una reserva activa.');
        await createOrOpenGame(reservationId);
      });
    });
    $('challenge-room').addEventListener('change', () => {
      resetChallengeForm();
      loadAdminChallenges().catch(report);
    });
    $('object-room').addEventListener('change', () => loadObjectUnlockChallenges().catch(report));
    $('refresh-challenges').addEventListener('click', () => loadAdminChallenges().catch(report));
    $('challenge-type').addEventListener('change', refreshChallengeType);
    refreshChallengeType();

    $('login-form').addEventListener('submit', event => {
      event.preventDefault();
      busy(event.currentTarget, async () => {
        const data = await api.login({ email: $('login-email').value.trim(), password: $('login-password').value });
        if (!data?.access_token || !data?.usuario || !['JUGADOR','ADMIN'].includes(data.usuario.rol)) throw new Error('Respuesta de login incompleta o con rol desconocido.');
        api.setToken(data.access_token); state.user = data.usuario; showPanels();
        $('login-password').value = '';
        message(isAdmin() ? `Bienvenido/a, ${state.user.nombre}. Tu cuenta ADMIN configura las salas. Para reservar y jugar, entra con una cuenta JUGADOR.` : `Bienvenido/a, ${state.user.nombre}. Puedes reservar y jugar desde tu panel.`, 'success');
        if (isPlayer()) {
          const loads = await Promise.allSettled([loadRooms(), loadGames(), loadReservations()]);
          loads.forEach(result => { if (result.status === 'rejected') report(result.reason); });
        }
        else { await Promise.all([loadRooms(), loadResults()]); if ($('challenge-room').value) await loadAdminChallenges(); }
      });
    });
    $('register-form').addEventListener('submit', event => {
      event.preventDefault();
      busy(event.currentTarget, async () => {
        await api.register({ nombre: $('register-name').value.trim(), email: $('register-email').value.trim(), password: $('register-password').value });
        const email = $('register-email').value.trim();
        $('register-form').reset(); $('login-email').value = email;
        message('Cuenta creada correctamente. Ya puedes iniciar sesión.', 'success');
      });
    });
    $('booking-form').addEventListener('submit', event => {
      event.preventDefault();
      busy(event.currentTarget, async () => {
        const sesion_id = positiveInt($('booking-session').value), numero_jugadores = positiveInt($('booking-players').value);
        const fecha = $('booking-date').value;
        if (!fecha) throw new Error('Selecciona una fecha antes de reservar.');
        if (!sesion_id || !numero_jugadores || numero_jugadores < 2) throw new Error('Selecciona una sesión e indica al menos 2 jugadores.');
        const selectedSession = state.sessions.find(s => Number(s.id) === sesion_id);
        if (!selectedSession || selectedSession.fecha !== fecha) throw new Error('La sesión no corresponde con la fecha seleccionada. Elige de nuevo la sesión.');
        const room = state.rooms.find(r => String(r.id) === $('booking-room').value);
        if (!room || numero_jugadores > Number(room.capacidad)) throw new Error(`La capacidad máxima de esta sala es ${room?.capacidad ?? 'desconocida'}.`);
        await api.book({ sesion_id, numero_jugadores });
        message('Reserva realizada correctamente y guardada en la base de datos.', 'success');
        await Promise.all([loadReservations(), loadSessions(), loadGames()]);
      });
    });
    $('room-form').addEventListener('submit', event => {
      event.preventDefault();
      busy(event.currentTarget, async () => {
        const capacidad = positiveInt($('room-capacity').value), duracion_minutos = positiveInt($('room-duration').value);
        if (!capacidad || capacidad < 2 || !duracion_minutos) throw new Error('La duración debe ser positiva y la capacidad al menos 2.');
        const body = { nombre: $('room-name').value.trim(), tematica: $('room-theme').value.trim(), dificultad: $('room-difficulty').value, duracion_minutos, capacidad, activa: true };
        if (!body.nombre || !body.tematica) throw new Error('Completa el nombre y la temática.');
        const editId = $('room-form').dataset.editId;
        if (editId) await api.updateRoom(editId, body);
        else await api.addRoom(body);
        resetRoomForm(); message(editId ? 'Sala actualizada.' : 'Sala creada y guardada.', 'success');
        await loadRooms();
      });
    });
    $('session-form').addEventListener('submit', event => {
      event.preventDefault();
      busy(event.currentTarget, async () => {
        const sala_id = positiveInt($('session-room').value), fecha = $('session-date').value, hora_inicio = $('session-time').value;
        if (!sala_id || !fecha || !hora_inicio) throw new Error('Selecciona sala, fecha y hora.');
        await api.addSession({ sala_id, fecha, hora_inicio });
        message('Sesión creada y guardada.', 'success');
        $('session-form').reset();
      });
    });
    $('result-form').addEventListener('submit', event => {
      event.preventDefault();
      busy(event.currentTarget, async () => {
        const sesion_id = positiveInt($('result-session').value), nombre_equipo = $('result-team').value.trim();
        const raw = $('result-time').value, tiempo_minutos = raw === '' ? null : Number(raw), superada = $('result-won').checked;
        if (!sesion_id || !nombre_equipo || (tiempo_minutos != null && (!Number.isSafeInteger(tiempo_minutos) || tiempo_minutos < 0))) throw new Error('Revisa los datos del resultado.');
        await api.addResult({ sesion_id, nombre_equipo, tiempo_minutos, superada });
        $('result-form').reset(); message('Resultado registrado.', 'success'); await loadResults();
      });
    });
  }
  hookup(); hookupGameForms(); showPanels(); loadRooms().catch(report);
})();
