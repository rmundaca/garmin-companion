'use strict';

/* ------------------------------------------------------------------ i18n */

const I18N = {
    es: {
        locale: 'es-ES',
        tabToday: 'Hoy', tabPlan: 'Plan', tabProgress: 'Progreso',
        connect: 'Conectar Garmin', settings: 'Ajustes', close: 'Cerrar', cancel: 'Cancelar',
        save: 'Guardar', back: 'Atrás', next: 'Siguiente', confirm: 'Confirmar', retry: 'Reintentar',
        today: 'Hoy', tomorrow: 'Mañana', yesterday: 'Ayer',
        daysShort: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        emptyTitle: 'Tu próximo objetivo empieza aquí',
        emptyText: 'Crea un plan para tu carrera. Los entrenamientos se envían solos a tu reloj Garmin.',
        loadErrorTitle: 'No se pudo cargar tu plan',
        loadErrorText: 'Falló la conexión con el servidor. Tu plan y tu progreso siguen guardados.',
        createPlan: 'Crear plan', newPlan: 'Nuevo plan',
        daysToRace: 'días para la carrera', raceDay: '¡Hoy es la carrera!',
        weekOf: 'Semana {w} de {n}', weekN: 'Semana {w}', sessionsDone: '{d} de {n} sesiones',
        prediction: 'Predicción', nextWorkout: 'Próximo entrenamiento', thisWeek: 'Esta semana',
        noUpcoming: 'No quedan sesiones pendientes en este plan.',
        compliance: 'Cumplimiento', vdot: 'Forma',
        adhSessions: 'Sesiones', adhKm: 'Kilómetros', adhPace: 'Ritmo',
        adhOf: '{d} de {n}', adhKmOf: '{d} de {n} km',
        adhPaceDetail: '{ok} en rango · {near} cerca · {off} fuera',
        adhEmpty: 'Aparecerá cuando completes o se te pase tu primera sesión.',
        adhNoPace: 'Sin datos de ritmo todavía',
        byType: 'Por tipo de sesión',
        formTitle: 'Tu forma', formPlan: 'Forma del plan', formEstimate: 'Forma estimada', formGarmin: 'VO2max Garmin',
        formSessions: '{n} sesiones de calidad', formNeeds: 'Necesita 3 sesiones de calidad en 6 semanas',
        formAbove: 'Tus sesiones de calidad recientes rinden como una forma de {f}: {d} puntos por encima de la del plan.',
        formBelow: 'Tus sesiones de calidad recientes rinden como una forma de {f}: {d} puntos por debajo de la del plan.',
        formSame: 'Tu forma estimada coincide con la del plan.',
        formGradual: 'La revisión periódica ajusta la forma del plan poco a poco (máx. ±1 punto por revisión).',
        formLegendPlan: 'Forma del plan', formLegendSession: 'Estimado por sesión',
        formChartHint: 'Desde el inicio del plan · toca o pasa el cursor para ver cada fecha',
        formNotStarted: 'El gráfico aparecerá cuando empiece el plan.',
        sumForm: 'Tu forma', sumFormEst: 'En tus sesiones: {v}', sumFormPlan: 'Con ella se fijan tus ritmos',
        sumRace: 'Previsión {d}', sumLoad: 'Carga', sumLoadBuilding: 'Calculándose',
        seeDetail: 'Ver detalle', progressError: 'No se pudo cargar tu progreso.',
        formWhat: 'Tu forma es un número que sale de tus tiempos (el VDOT de Jack Daniels): cuanto más alto, más rápido corres. Con ella se calculan tus ritmos y la previsión de tu carrera.',
        predTitle: 'Predicciones', predDistance: 'Distancia', predPlan: 'Con la forma del plan', predForm: 'Con tu forma estimada',
        predTarget: 'objetivo', predNote: 'La distancia objetivo incluye el desnivel del recorrido; las demás, en llano.',
        garminNote: 'Garmin estima el VO2max con la frecuencia cardiaca; suele ser más alto que tu forma, que sale de tus tiempos.',
        aeroTitle: 'Base aeróbica',
        effTitle: 'Eficiencia en rodajes', effUnit: 'm por latido', effLabel: 'Metros por latido',
        effUp: '▲ {pct}% desde el inicio del plan', effDown: '▼ {pct}% desde el inicio del plan', effFlat: 'Estable desde el inicio del plan',
        effHint: 'Metros que avanzas por cada latido en rodajes y tiradas largas. Si sube, corres más con el mismo esfuerzo cardiaco. El calor, las cuestas o el cansancio la bajan puntualmente.',
        effNeeds: 'Necesita al menos 4 rodajes con pulso registrado.',
        effLegendRun: 'Cada rodaje', effLegendTrend: 'Tendencia',
        mixTitle: 'Intensidad · últimas 4 semanas',
        mixEasy: 'Fácil', mixModerate: 'Moderado', mixHard: 'Intenso',
        mixOk: '✓ Buen equilibrio: {pct}% del tiempo en fácil.',
        mixHigh: '▲ Demasiada intensidad: {pct}% del tiempo en fácil. Lo ideal ronda el 80%.',
        mixGrey: 'El {pct}% son rodajes corridos demasiado rápido: esa "zona gris" cansa sin dar el beneficio de la calidad.',
        mixEmpty: 'Aparecerá cuando completes sesiones en las últimas 4 semanas.',
        mixMinutes: '{n} min en total',
        loadTitle: 'Carga de entrenamiento',
        loadZone: { low: 'Carga baja', optimal: 'Zona óptima', caution: 'Precaución', high: 'Riesgo alto' },
        loadVs: {
            up: 'Tu carga de los últimos 7 días está un {pct}% por encima de tu media de las últimas 4 semanas.',
            down: 'Tu carga de los últimos 7 días está un {pct}% por debajo de tu media de las últimas 4 semanas.',
            same: 'Tu carga de los últimos 7 días está en línea con tu media de las últimas 4 semanas.',
        },
        loadAdvice: {
            low: 'Es normal en semanas de descarga, de afinamiento o a mitad de semana.',
            caution: 'Evita añadir kilómetros extra esta semana.',
            high: 'Subiste la carga de golpe: prioriza el descanso y los rodajes suaves.',
        },
        loadBuilding: 'Se calcula con al menos 3 semanas de entrenamiento registrado. Disponible en {n} días.',
        loadChart: 'Desde {d} · franja = zona óptima (0,8–1,3)',
        loadAbout: 'Carga = minutos × esfuerzo percibido. Si no indicas el esfuerzo tras la sesión, se estima según el tipo de sesión.',
        paceLevel: {
            ok: 'Ritmo en rango', near_fast: 'Algo rápido', near_slow: 'Algo lento',
            off_fast: 'Demasiado rápido', off_slow: 'Demasiado lento',
        },
        paceCompare: 'Previsto {e}/km · real {a}/km',
        paceDiff: { fast: '{pct}% más rápido', slow: '{pct}% más lento' },
        paceTip: {
            easy_fast: 'En los rodajes, ir más lento te ayuda a recuperar y a construir base aeróbica.',
            mean: 'Se compara el ritmo medio de toda la sesión, incluidos calentamiento y recuperaciones. Si la corres con el entrenamiento del reloj, se medirán solo los bloques de trabajo.',
            work: 'Se compara solo el ritmo de los bloques de trabajo, sin calentamiento ni recuperaciones.',
        },
        workBlocks: 'Bloques de trabajo', gapShort: 'en llano {p}',
        workFade: 'Las últimas salieron un {pct}% más lentas que las primeras.',
        workEven: 'Ritmo sostenido de principio a fin.',
        onWatch: 'En el reloj', willSync: 'Se enviará al reloj unos días antes',
        notConnected: 'Garmin no conectado',
        pendingSync: '{n} sesiones de los próximos días aún no están en el reloj.',
        syncing: 'Enviando entrenamientos al reloj…',
        synced: 'Enviado al reloj: {n} sesiones.',
        syncNow: 'Sincronizar ahora',
        syncHint: 'Importa tus últimas carreras de Garmin Connect y envía al reloj las próximas sesiones.',
        syncResult: 'Sesiones completadas: {a}. Enviado al reloj: {n}.',
        weekVolume: 'Volumen semanal (km)',
        volPlanned: 'Planificado', volReal: 'Realizado', volLight: 'Descarga / afinamiento',
        volDone: '{d} km de {p} planificados', volFuture: '{p} km planificados',
        volExtra: 'incluye {e} km fuera del plan', seeWeek: 'Ver sesiones',
        cancelPlan: 'Cancelar plan',
        cancelPlanMsg: 'Se quitarán del reloj las sesiones pendientes. El historial se conserva.',
        finishPlan: 'Finalizar plan',
        finishPlanMsg: 'El plan pasará al historial como completado. Después podrás crear uno nuevo.',
        newPlanMsg: 'Crear un plan nuevo cancela el plan actual y quita del reloj sus sesiones pendientes.',
        newPlanFinishedMsg: 'Crear un plan nuevo finaliza el actual y lo guarda en el historial como completado.',
        planCancelled: 'Plan cancelado',
        planFinished: 'Plan completado',
        history: 'Historial', historyOpen: 'Ver planes anteriores',
        historyHint: 'Tus planes terminados: cumplimiento, evolución de tu forma y resultado de la carrera.',
        historyEmpty: 'Todavía no tienes planes terminados.',
        planStatus: { completed: 'Completado', cancelled: 'Cancelado' },
        histWeeks: '{n} semanas', histReviews: '{n} revisiones aceptadas',
        histRace: 'Carrera', histPredicted: 'previsto {p}',
        histSessions: 'Sesiones', histPace: 'Ritmo en rango',
        phase: { base: 'Base', build: 'Construcción', peak: 'Pico', deload: 'Descarga', tuneup: 'Carrera B', taper: 'Afinamiento', race: 'Carrera' },
        type: { easy: 'Suave', long_run: 'Tirada larga', tempo: 'Tempo', intervals: 'Series', hills: 'Cuestas', race: 'Carrera' },
        about: {
            easy: 'Rodaje suave: base aeróbica y recuperación. Si dudas, ve más lento.',
            long_run: 'Tirada larga: resistencia. El ritmo es suave; lo que importa es el tiempo en pie.',
            tempo: 'Tempo: ritmo umbral, "cómodamente duro". Podrías sostenerlo cerca de una hora.',
            intervals: 'Series: mejoran tu VO2max. Rápidas pero controladas; la última debe salir igual que la primera.',
            hills: 'Cuestas: fuerza y técnica. Se corren por esfuerzo, no por ritmo.',
            race: 'Día de carrera. Confía en el trabajo hecho.',
        },
        status: { scheduled: 'Pendiente', completed: 'Hecha', missed: 'No realizada' },
        steps: 'Pasos', actual: 'Tu carrera',
        move: 'Mover', moveTo: 'Nueva fecha', moved: 'Sesión movida',
        markDone: 'Marcar como hecha', unmarkDone: 'Desmarcar',
        // Session and account
        loginTitle: 'Entra con tu cuenta Garmin',
        loginText: 'Cada persona entra con su propia cuenta Garmin. Tus planes y datos son solo tuyos.',
        signOut: 'Cerrar sesión', reconnect: 'Reconectar Garmin',
        garminExpired: 'La sesión de Garmin expiró. Reconecta para seguir enviando entrenamientos.',
        deleteAccount: 'Borrar mi cuenta y mis datos',
        deleteAccountMsg: 'Se borrarán tus planes, actividades y el acceso a Garmin guardado en este servidor. No se puede deshacer.',
        accountDeleted: 'Cuenta borrada',
        volumeAdjusted: 'Volumen ajustado al {pct}% del plan original',
        // Review
        reviewTitle: 'Revisión de las semanas {a}–{b}', reviewTitleOne: 'Revisión de la semana {a}',
        reviewMetrics: '{c} de {p} sesiones · {kd} de {kp} km',
        qFatigue: '¿Cómo te sientes?', fatigueOpt: { good: 'Bien', tired: 'Cansado', very_tired: 'Muy cansado' },
        qPain: '¿Alguna molestia o dolor?', painOpt: { no: 'No', mild: 'Leve', yes: 'Sí' },
        seeProposal: 'Ver propuesta', skip: 'Omitir',
        proposalTitle: 'Propuesta para las próximas semanas', keepPlan: 'Mantener plan', accept: 'Aceptar', gotIt: 'Entendido',
        reason: {
            compliance_low: 'Completaste el {pct}% de las sesiones.',
            fatigue: 'Te sientes cansado.',
            fatigue_high: 'Te sientes muy cansado.',
            pain: 'Tienes dolor: esta semana pasa a ser de descarga. Si persiste, consulta a un profesional.',
            pain_mild: 'Tienes una molestia leve.',
            recovering: 'Vas bien: el volumen vuelve poco a poco a lo planificado.',
            quality_fast: 'Tus sesiones de calidad fueron un {pct}% más rápidas de lo previsto, sin gran esfuerzo.',
            quality_slow: 'Tus sesiones de calidad fueron un {pct}% más lentas de lo previsto.',
            all_good: 'Cumpliste el plan y te sientes bien. Sigue así.',
            load_spike: 'Tu carga de los últimos 7 días es {ratio} veces tu media de 4 semanas: un salto así aumenta el riesgo de lesión.',
        },
        tip: {
            easy_too_fast: 'Tus rodajes suaves van un {pct}% más rápidos de lo previsto. Ir más lento te ayuda a recuperar.',
            easy_comfortable: 'Tus rodajes suaves van un {pct}% más rápidos de lo previsto y te resultan cómodos (esfuerzo {rpe}/10). Probablemente tu forma real supera la del plan ({vdot}): actualiza tu marca de referencia en Ajustes para ajustar todos los ritmos.',
            aerobic_ahead: 'Tus rodajes van un {pct}% más rápidos de lo previsto y cómodos, pero tus series y tempos van un {q}% más lentos. Tu base aeróbica va por delante de tu velocidad: mantén la forma del plan y deja que las sesiones de calidad marquen cuándo subirla.',
            fade: 'En tus series, las últimas repeticiones salen un {pct}% más lentas que las primeras. Sal más controlado: la última debe salir igual que la primera.',
            efficiency_up: 'Tu eficiencia aeróbica mejoró un {pct}%: corres más rápido con el mismo pulso. La base está funcionando.',
            efficiency_down: 'Tu eficiencia aeróbica bajó un {pct}%. Puede ser fatiga acumulada, calor o poco descanso: vigila cómo te recuperas.',
            load_high: 'Tu carga reciente está algo por encima de lo habitual ({ratio}×). Evita añadir kilómetros extra.',
            form_above: 'Tus sesiones de calidad rinden como una forma de {form} (el plan usa {vdot}). Si se mantiene, las próximas revisiones la subirán.',
            form_below: 'Tus sesiones de calidad rinden como una forma de {form} (el plan usa {vdot}). Si te cuestan, prioriza terminarlas antes que el ritmo.',
        },
        chVdot: 'Forma {a} → {b} · predicción {pa} → {pb}',
        chVolume: 'Volumen al {pct}% del plan original',
        chDeload: 'Esta semana pasa a ser de descarga',
        reviewApplied: 'Plan ajustado', reviewKept: 'Plan sin cambios',
        // B races
        races: 'Carreras de preparación', raceAdd: 'Añadir carrera',
        racesHint: 'Otras carreras antes de tu objetivo. El plan se ajusta solo: días suaves antes y después, y la semana de la carrera es más ligera.',
        raceAddHint: 'Entre la semana 2 y el inicio del afinamiento, y con al menos 2 semanas entre carreras.',
        raceNameHint: 'Ej.: 10K del barrio',
        raceAdded: 'Carrera añadida. Plan ajustado.', raceDeleted: 'Carrera quitada. Plan ajustado.',
        raceDelete: 'Quitar carrera', raceDeleteMsg: 'El plan vuelve a quedar como antes de añadirla.',
        raceResult: 'Tu tiempo: {t}',
        raceProposalTitle: 'Resultado de tu carrera de preparación',
        raceProposalText: '{name}: {t}. Con ese tiempo tu forma pasa de {a} a {b}.',
        raceProposalAsk: '¿Ajustamos los ritmos del plan y tu marca de referencia a esta carrera?',
        raceVdotApplied: 'Ritmos actualizados', raceVdotKept: 'Ritmos sin cambios', updatePaces: 'Actualizar ritmos',
        // Effort
        rpeQuestion: '¿Qué tal fue: {title}?', rpeLabel: 'Esfuerzo percibido',
        rpeOpt: { 3: 'Fácil', 5: 'Moderado', 7: 'Duro', 9: 'Muy duro' }, rpeSaved: 'Guardado',
        // Wizard
        wizTitle: 'Nuevo plan', wizStep: 'Paso {s} de 3',
        wizRace: 'Tu carrera', wizWeek: 'Tu semana', wizMark: 'Tu nivel actual',
        distance: 'Distancia', raceDate: 'Fecha de la carrera', startDate: 'Empiezas el',
        eventName: 'Nombre del evento (opcional)', eventNameHint: 'Ej.: Maratón de Santiago',
        terrain: 'Recorrido', terrainOpt: { flat: 'Llano', rolling: 'Ondulado', hilly: 'Con cuestas' },
        runDays: '¿Qué días puedes correr?', longRunDay: 'Día de la tirada larga',
        level: 'Experiencia',
        levelOpt: { beginner: 'Empiezo a correr', intermediate: 'Corro habitualmente', advanced: 'Hago series y carreras', elite: 'Muy experimentado' },
        injury: 'Lesiones', injuryOpt: { rarely_never: 'Casi nunca', minor_past: 'Alguna pasada', frequent_recent: 'Frecuentes o recientes' },
        refMark: 'Tu mejor marca reciente', refTime: 'Tiempo (mm:ss o h:mm:ss)',
        refHint: 'Con esta marca se calculan tus ritmos. Mejor una reciente que tu mejor marca de hace años.',
        fromGarmin: 'Sugerida desde tus récords de Garmin',
        weeksInfo: '{w} semanas', weeksRec: 'Recomendado: {min}–{max} semanas',
        weeksShort: 'Es poco tiempo para esta distancia. El plan será más exigente.',
        estimated: 'Tiempo estimado', pace: 'Ritmo',
        creating: 'Creando…', planCreated: 'Plan creado',
        // Settings
        garminAccount: 'Cuenta Garmin', connectedAs: 'Cuenta: {n}',
        language: 'Idioma', languageHint: 'También se usa en los entrenamientos del reloj.',
        theme: 'Tema', themeOpt: { system: 'Sistema', light: 'Claro', dark: 'Oscuro' },
        themeHint: 'Se guarda en este dispositivo.',
        palette: 'Colores', paletteOpt: { classic: 'Clásica', track: 'Pista', volt: 'Volt', dawn: 'Amanecer' },
        pendingDeletions: '{n} entrenamientos pendientes de quitar de Garmin. Se reintenta cada hora; si no se resuelve, reconecta Garmin o usa "Limpiar calendario de Garmin" en Avanzado.',
        paces: 'Tus ritmos', updateMark: 'Actualizar marca', marksUpdated: 'Ritmos actualizados',
        paceNames: { easy: 'Suave', marathon: 'Maratón', threshold: 'Umbral', interval: 'Series', repetition: 'Repeticiones' },
        helpOpen: 'Cómo funciona',
        advanced: 'Avanzado',
        cleanCalendar: 'Limpiar calendario de Garmin',
        cleanHint: 'Quita del calendario de Garmin los entrenamientos futuros creados por esta app (incluidos restos de versiones anteriores) y vuelve a enviar los próximos días. No toca otros entrenamientos.',
        cleanDone: 'Se quitaron {n} entrenamientos',
        database: 'Base de datos',
        backupHint: 'Descarga una copia de todos los datos de la app (todos los perfiles de este servidor) o restaura una copia anterior.',
        backupDownload: 'Descargar copia', backupRestore: 'Restaurar copia…',
        restoreTitle: 'Restaurar base de datos',
        restoreMsg: 'Se sustituirán todos los datos actuales (de todos los perfiles) por los de "{f}". Se guarda una copia de los datos actuales en el servidor por si acaso.',
        restoring: 'Restaurando…', restored: 'Base de datos restaurada',
        // Connection
        email: 'Email de Garmin', password: 'Contraseña', signIn: 'Entrar',
        loginHint: 'La contraseña no se guarda: solo se usa para obtener un token de sesión en este servidor.',
        mfaTitle: 'Código de verificación', mfaHint: 'Garmin te envió un código por email o SMS.', verify: 'Verificar',
        useLogin: 'O entra con email y contraseña',
        tokenHint: 'Genera garmin_tokens_(tu email).json en tu PC con generate_token.py y súbelo aquí.',
        tokenFile: 'Archivo garmin_tokens_(email).json', tokenPaste: 'o pega su contenido',
        connected: 'Garmin conectado',
        err: {
            network: 'No se pudo contactar con el servidor.',
            login_failed: 'Garmin rechazó el inicio de sesión. Revisa email y contraseña, o usa un token.',
            mfa_expired: 'El código expiró. Vuelve a iniciar sesión.',
            mfa_failed: 'Código incorrecto.',
            invalid_token_json: 'El archivo no es un JSON válido.',
            invalid_token: 'Garmin no aceptó el token: caducó o ya se usó en otro lugar. Genera uno nuevo y súbelo enseguida, o entra con email y contraseña.',
            garmin_not_connected: 'Garmin no está conectado.',
            clean_failed: 'No se pudo limpiar el calendario de Garmin.',
            plan_too_short: 'Necesitas al menos 4 semanas hasta la carrera.',
            plan_too_long: 'El plan no puede superar las 30 semanas.',
            start_in_past: 'La fecha de inicio no puede ser anterior a hoy.',
            invalid_days: 'Elige al menos 2 días.',
            invalid_time: 'Revisa el tiempo de tu marca.',
            workout_completed: 'Esa sesión ya está hecha.',
            not_authenticated: 'Tu sesión terminó. Vuelve a entrar.',
            review_pending: 'Ya hay una propuesta pendiente.',
            no_review_due: 'No hay revisión pendiente.',
            invalid_backup: 'El archivo no es una copia válida de Garmin Companion.',
            backup_too_large: 'El archivo es demasiado grande.',
            admin_only: 'Solo el administrador del servidor puede hacer esto.',
            invalid_date: 'Elige una fecha entre hoy y el día de la carrera.',
            b_race_in_past: 'La carrera debe ser a partir de mañana.',
            b_race_too_early: 'Esa fecha cae en la primera semana del plan. Elige una posterior.',
            b_race_too_late: 'Esa fecha cae en el afinamiento o en la semana de tu carrera objetivo.',
            b_race_too_close: 'Deja al menos 2 semanas entre carreras de preparación.',
            race_not_found: 'Esa carrera ya no existe.',
            no_race_result: 'No hay un tiempo válido de esa carrera.',
            generic: 'Algo salió mal. Inténtalo de nuevo.',
        },
    },
    en: {
        locale: 'en-GB',
        tabToday: 'Today', tabPlan: 'Plan', tabProgress: 'Progress',
        connect: 'Connect Garmin', settings: 'Settings', close: 'Close', cancel: 'Cancel',
        save: 'Save', back: 'Back', next: 'Next', confirm: 'Confirm', retry: 'Retry',
        today: 'Today', tomorrow: 'Tomorrow', yesterday: 'Yesterday',
        daysShort: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        emptyTitle: 'Your next goal starts here',
        emptyText: 'Create a plan for your race. Workouts are sent to your Garmin watch automatically.',
        loadErrorTitle: 'Your plan could not be loaded',
        loadErrorText: 'The connection to the server failed. Your plan and progress are still saved.',
        createPlan: 'Create plan', newPlan: 'New plan',
        daysToRace: 'days to race day', raceDay: 'Race day is today!',
        weekOf: 'Week {w} of {n}', weekN: 'Week {w}', sessionsDone: '{d} of {n} sessions',
        prediction: 'Prediction', nextWorkout: 'Next workout', thisWeek: 'This week',
        noUpcoming: 'No sessions left in this plan.',
        compliance: 'Compliance', vdot: 'Fitness',
        adhSessions: 'Sessions', adhKm: 'Kilometres', adhPace: 'Pace',
        adhOf: '{d} of {n}', adhKmOf: '{d} of {n} km',
        adhPaceDetail: '{ok} on target · {near} close · {off} off',
        adhEmpty: 'Shows up once your first session is done or missed.',
        adhNoPace: 'No pace data yet',
        byType: 'By session type',
        formTitle: 'Your fitness', formPlan: 'Plan fitness', formEstimate: 'Estimated fitness', formGarmin: 'Garmin VO2max',
        formSessions: '{n} quality sessions', formNeeds: 'Needs 3 quality sessions within 6 weeks',
        formAbove: 'Your recent quality sessions perform like a fitness of {f}: {d} points above the plan.',
        formBelow: 'Your recent quality sessions perform like a fitness of {f}: {d} points below the plan.',
        formSame: 'Your estimated fitness matches the plan.',
        formGradual: 'The periodic review adjusts the plan fitness gradually (max ±1 point per review).',
        formLegendPlan: 'Plan fitness', formLegendSession: 'Estimated per session',
        formChartHint: 'Since the plan started · tap or hover to see each date',
        formNotStarted: 'The chart appears once the plan starts.',
        sumForm: 'Your fitness', sumFormEst: 'In your sessions: {v}', sumFormPlan: 'Your paces are based on it',
        sumRace: '{d} forecast', sumLoad: 'Load', sumLoadBuilding: 'Building up',
        seeDetail: 'See details', progressError: 'Your progress could not be loaded.',
        formWhat: 'Your fitness is a number derived from your race times (Jack Daniels’ VDOT): the higher it is, the faster you run. Your paces and race forecast are calculated from it.',
        predTitle: 'Predictions', predDistance: 'Distance', predPlan: 'With plan fitness', predForm: 'With estimated fitness',
        predTarget: 'goal', predNote: 'The goal distance includes the course elevation; the others assume flat.',
        garminNote: 'Garmin estimates VO2max from heart rate; it is usually higher than your fitness, which comes from your times.',
        aeroTitle: 'Aerobic base',
        effTitle: 'Easy-run efficiency', effUnit: 'm per heartbeat', effLabel: 'Metres per heartbeat',
        effUp: '▲ {pct}% since the plan started', effDown: '▼ {pct}% since the plan started', effFlat: 'Stable since the plan started',
        effHint: 'Metres covered per heartbeat on easy and long runs. If it rises, you run further for the same cardiac effort. Heat, hills or fatigue lower it temporarily.',
        effNeeds: 'Needs at least 4 easy runs with heart rate.',
        effLegendRun: 'Each run', effLegendTrend: 'Trend',
        mixTitle: 'Intensity · last 4 weeks',
        mixEasy: 'Easy', mixModerate: 'Moderate', mixHard: 'Hard',
        mixOk: '✓ Good balance: {pct}% of your time was easy.',
        mixHigh: '▲ Too much intensity: {pct}% of your time was easy. Aim for about 80%.',
        mixGrey: '{pct}% comes from easy runs done too fast: that "grey zone" tires you without the benefit of quality work.',
        mixEmpty: 'Shows up once you complete sessions in the last 4 weeks.',
        mixMinutes: '{n} min in total',
        loadTitle: 'Training load',
        loadZone: { low: 'Low load', optimal: 'Optimal zone', caution: 'Caution', high: 'High risk' },
        loadVs: {
            up: 'Your load over the last 7 days is {pct}% above your average of the last 4 weeks.',
            down: 'Your load over the last 7 days is {pct}% below your average of the last 4 weeks.',
            same: 'Your load over the last 7 days is in line with your average of the last 4 weeks.',
        },
        loadAdvice: {
            low: 'Normal in recovery or taper weeks, or midway through a week.',
            caution: 'Avoid adding extra kilometres this week.',
            high: 'Your load jumped suddenly: prioritise rest and easy runs.',
        },
        loadBuilding: 'Needs at least 3 weeks of logged training. Available in {n} days.',
        loadChart: 'Since {d} · band = optimal zone (0.8–1.3)',
        loadAbout: 'Load = minutes × perceived effort. Sessions you do not rate get an effort estimated from their type.',
        paceLevel: {
            ok: 'Pace on target', near_fast: 'A bit fast', near_slow: 'A bit slow',
            off_fast: 'Too fast', off_slow: 'Too slow',
        },
        paceCompare: 'Planned {e}/km · actual {a}/km',
        paceDiff: { fast: '{pct}% faster', slow: '{pct}% slower' },
        paceTip: {
            easy_fast: 'On easy runs, going slower helps you recover and build your aerobic base.',
            mean: 'Compares the average pace of the whole session, including warm-up and recoveries. Run it with the watch workout to measure only the work blocks.',
            work: 'Compares only the pace of the work blocks, without warm-up or recoveries.',
        },
        workBlocks: 'Work blocks', gapShort: 'flat {p}',
        workFade: 'The last reps were {pct}% slower than the first.',
        workEven: 'Pace held from start to finish.',
        onWatch: 'On your watch', willSync: 'Will be sent to your watch a few days before',
        notConnected: 'Garmin not connected',
        pendingSync: '{n} upcoming sessions are not on your watch yet.',
        syncing: 'Sending workouts to your watch…',
        synced: 'Sent to your watch: {n} sessions.',
        syncNow: 'Sync now',
        syncHint: 'Imports your latest runs from Garmin Connect and sends the next sessions to your watch.',
        syncResult: 'Sessions completed: {a}. Sent to your watch: {n}.',
        weekVolume: 'Weekly volume (km)',
        volPlanned: 'Planned', volReal: 'Done', volLight: 'Recovery / taper',
        volDone: '{d} km of {p} planned', volFuture: '{p} km planned',
        volExtra: 'includes {e} km outside the plan', seeWeek: 'See sessions',
        cancelPlan: 'Cancel plan',
        cancelPlanMsg: 'Pending sessions will be removed from your watch. History is kept.',
        finishPlan: 'Finish plan',
        finishPlanMsg: 'The plan will move to your history as completed. You can then create a new one.',
        newPlanMsg: 'Creating a new plan cancels the current one and removes its pending sessions from your watch.',
        newPlanFinishedMsg: 'Creating a new plan finishes the current one and saves it to your history as completed.',
        planCancelled: 'Plan cancelled',
        planFinished: 'Plan completed',
        history: 'History', historyOpen: 'See past plans',
        historyHint: 'Your finished plans: compliance, fitness progress and race result.',
        historyEmpty: 'You have no finished plans yet.',
        planStatus: { completed: 'Completed', cancelled: 'Cancelled' },
        histWeeks: '{n} weeks', histReviews: '{n} reviews accepted',
        histRace: 'Race', histPredicted: 'predicted {p}',
        histSessions: 'Sessions', histPace: 'Pace on target',
        phase: { base: 'Base', build: 'Build', peak: 'Peak', deload: 'Recovery', tuneup: 'Tune-up race', taper: 'Taper', race: 'Race' },
        type: { easy: 'Easy', long_run: 'Long run', tempo: 'Tempo', intervals: 'Intervals', hills: 'Hills', race: 'Race' },
        about: {
            easy: 'Easy run: aerobic base and recovery. When in doubt, go slower.',
            long_run: 'Long run: endurance. Keep it easy; time on feet is what counts.',
            tempo: 'Tempo: threshold pace, "comfortably hard". You could hold it for about an hour.',
            intervals: 'Intervals: build VO2max. Fast but controlled; the last rep should match the first.',
            hills: 'Hills: strength and form. Run them by effort, not pace.',
            race: 'Race day. Trust the work you have done.',
        },
        status: { scheduled: 'Upcoming', completed: 'Done', missed: 'Missed' },
        steps: 'Steps', actual: 'Your run',
        move: 'Move', moveTo: 'New date', moved: 'Session moved',
        markDone: 'Mark as done', unmarkDone: 'Unmark',
        loginTitle: 'Sign in with your Garmin account',
        loginText: 'Everyone signs in with their own Garmin account. Your plans and data are yours only.',
        signOut: 'Sign out', reconnect: 'Reconnect Garmin',
        garminExpired: 'Your Garmin session expired. Reconnect to keep sending workouts.',
        deleteAccount: 'Delete my account and data',
        deleteAccountMsg: 'Your plans, activities and the Garmin access stored on this server will be deleted. This cannot be undone.',
        accountDeleted: 'Account deleted',
        volumeAdjusted: 'Volume adjusted to {pct}% of the original plan',
        reviewTitle: 'Review of weeks {a}–{b}', reviewTitleOne: 'Review of week {a}',
        reviewMetrics: '{c} of {p} sessions · {kd} of {kp} km',
        qFatigue: 'How do you feel?', fatigueOpt: { good: 'Good', tired: 'Tired', very_tired: 'Very tired' },
        qPain: 'Any niggles or pain?', painOpt: { no: 'No', mild: 'Mild', yes: 'Yes' },
        seeProposal: 'See proposal', skip: 'Skip',
        proposalTitle: 'Proposal for the coming weeks', keepPlan: 'Keep plan', accept: 'Accept', gotIt: 'Got it',
        reason: {
            compliance_low: 'You completed {pct}% of sessions.',
            fatigue: 'You feel tired.',
            fatigue_high: 'You feel very tired.',
            pain: 'You have pain: this week becomes a recovery week. If it persists, see a professional.',
            pain_mild: 'You have a mild niggle.',
            recovering: 'Going well: volume gradually returns to the plan.',
            quality_fast: 'Your quality sessions were {pct}% faster than expected, without much effort.',
            quality_slow: 'Your quality sessions were {pct}% slower than expected.',
            all_good: 'You followed the plan and feel good. Keep it up.',
            load_spike: 'Your load over the last 7 days is {ratio} times your 4-week average: a jump like that raises injury risk.',
        },
        tip: {
            easy_too_fast: 'Your easy runs are {pct}% faster than expected. Slowing down helps you recover.',
            easy_comfortable: 'Your easy runs are {pct}% faster than expected and feel comfortable (effort {rpe}/10). Your real fitness probably exceeds the plan’s ({vdot}): update your reference result in Settings to adjust all paces.',
            aerobic_ahead: 'Your easy runs are {pct}% faster than expected and comfortable, but your intervals and tempos are {q}% slower. Your aerobic base is ahead of your speed: keep the plan fitness and let quality sessions show when to raise it.',
            fade: 'In your intervals, the last reps are {pct}% slower than the first. Start more controlled: the last rep should match the first.',
            efficiency_up: 'Your aerobic efficiency improved {pct}%: you run faster at the same heart rate. Your base is working.',
            efficiency_down: 'Your aerobic efficiency dropped {pct}%. It may be accumulated fatigue, heat or poor rest: watch your recovery.',
            load_high: 'Your recent load is somewhat above usual ({ratio}×). Avoid adding extra kilometres.',
            form_above: 'Your quality sessions perform like a fitness of {form} (the plan uses {vdot}). If it holds, upcoming reviews will raise it.',
            form_below: 'Your quality sessions perform like a fitness of {form} (the plan uses {vdot}). If they feel hard, finishing them matters more than pace.',
        },
        chVdot: 'Fitness {a} → {b} · prediction {pa} → {pb}',
        chVolume: 'Volume at {pct}% of the original plan',
        chDeload: 'This week becomes a recovery week',
        reviewApplied: 'Plan adjusted', reviewKept: 'Plan unchanged',
        races: 'Tune-up races', raceAdd: 'Add race',
        racesHint: 'Other races before your goal. The plan adjusts itself: easy days before and after, and a lighter race week.',
        raceAddHint: 'Between week 2 and the start of the taper, with at least 2 weeks between races.',
        raceNameHint: 'E.g. Local 10K',
        raceAdded: 'Race added. Plan adjusted.', raceDeleted: 'Race removed. Plan adjusted.',
        raceDelete: 'Remove race', raceDeleteMsg: 'The plan goes back to how it was before you added it.',
        raceResult: 'Your time: {t}',
        raceProposalTitle: 'Your tune-up race result',
        raceProposalText: '{name}: {t}. That time moves your fitness from {a} to {b}.',
        raceProposalAsk: 'Update the plan paces and your reference result to this race?',
        raceVdotApplied: 'Paces updated', raceVdotKept: 'Paces unchanged', updatePaces: 'Update paces',
        rpeQuestion: 'How was it: {title}?', rpeLabel: 'Perceived effort',
        rpeOpt: { 3: 'Easy', 5: 'Moderate', 7: 'Hard', 9: 'Very hard' }, rpeSaved: 'Saved',
        wizTitle: 'New plan', wizStep: 'Step {s} of 3',
        wizRace: 'Your race', wizWeek: 'Your week', wizMark: 'Your current level',
        distance: 'Distance', raceDate: 'Race date', startDate: 'Starting on',
        eventName: 'Event name (optional)', eventNameHint: 'E.g. Santiago Marathon',
        terrain: 'Course', terrainOpt: { flat: 'Flat', rolling: 'Rolling', hilly: 'Hilly' },
        runDays: 'Which days can you run?', longRunDay: 'Long run day',
        level: 'Experience',
        levelOpt: { beginner: 'New to running', intermediate: 'I run regularly', advanced: 'I do intervals and races', elite: 'Very experienced' },
        injury: 'Injuries', injuryOpt: { rarely_never: 'Rarely', minor_past: 'Some in the past', frequent_recent: 'Frequent or recent' },
        refMark: 'Your best recent result', refTime: 'Time (mm:ss or h:mm:ss)',
        refHint: 'Your paces are calculated from this. A recent result beats an old personal best.',
        fromGarmin: 'Suggested from your Garmin records',
        weeksInfo: '{w} weeks', weeksRec: 'Recommended: {min}–{max} weeks',
        weeksShort: 'That is short for this distance. The plan will be more demanding.',
        estimated: 'Estimated time', pace: 'Pace',
        creating: 'Creating…', planCreated: 'Plan created',
        garminAccount: 'Garmin account', connectedAs: 'Account: {n}',
        language: 'Language', languageHint: 'Also used for workouts on your watch.',
        theme: 'Theme', themeOpt: { system: 'System', light: 'Light', dark: 'Dark' },
        themeHint: 'Saved on this device.',
        palette: 'Colors', paletteOpt: { classic: 'Classic', track: 'Track', volt: 'Volt', dawn: 'Dawn' },
        pendingDeletions: '{n} workouts still need to be removed from Garmin. This is retried every hour; if it persists, reconnect Garmin or use "Clean Garmin calendar" under Advanced.',
        paces: 'Your paces', updateMark: 'Update result', marksUpdated: 'Paces updated',
        paceNames: { easy: 'Easy', marathon: 'Marathon', threshold: 'Threshold', interval: 'Interval', repetition: 'Repetition' },
        helpOpen: 'How it works',
        advanced: 'Advanced',
        cleanCalendar: 'Clean Garmin calendar',
        cleanHint: 'Removes future workouts created by this app from your Garmin calendar (including leftovers from older versions) and re-sends the next few days. Other workouts are untouched.',
        cleanDone: 'Removed {n} workouts',
        database: 'Database',
        backupHint: 'Download a copy of all app data (every profile on this server) or restore an earlier copy.',
        backupDownload: 'Download copy', backupRestore: 'Restore copy…',
        restoreTitle: 'Restore database',
        restoreMsg: 'All current data (for every profile) will be replaced with "{f}". A copy of the current data is kept on the server just in case.',
        restoring: 'Restoring…', restored: 'Database restored',
        email: 'Garmin email', password: 'Password', signIn: 'Sign in',
        loginHint: 'Your password is not stored: it is only used to obtain a session token on this server.',
        mfaTitle: 'Verification code', mfaHint: 'Garmin sent you a code by email or SMS.', verify: 'Verify',
        useLogin: 'Or sign in with email and password',
        tokenHint: 'Generate garmin_tokens_(your email).json on your PC with generate_token.py and upload it here.',
        tokenFile: 'garmin_tokens_(email).json file', tokenPaste: 'or paste its contents',
        connected: 'Garmin connected',
        err: {
            network: 'Could not reach the server.',
            login_failed: 'Garmin rejected the sign-in. Check email and password, or use a token.',
            mfa_expired: 'The code expired. Sign in again.',
            mfa_failed: 'Wrong code.',
            invalid_token_json: 'The file is not valid JSON.',
            invalid_token: 'Garmin did not accept the token: it expired or was already used elsewhere. Generate a new one and upload it right away, or sign in with email and password.',
            garmin_not_connected: 'Garmin is not connected.',
            clean_failed: 'Could not clean the Garmin calendar.',
            plan_too_short: 'You need at least 4 weeks before the race.',
            plan_too_long: 'Plans cannot be longer than 30 weeks.',
            start_in_past: 'The start date cannot be in the past.',
            invalid_days: 'Pick at least 2 days.',
            invalid_time: 'Check the time of your result.',
            workout_completed: 'That session is already done.',
            not_authenticated: 'Your session ended. Please sign in again.',
            review_pending: 'There is already a pending proposal.',
            no_review_due: 'No review is due.',
            invalid_backup: 'This file is not a valid Garmin Companion backup.',
            backup_too_large: 'The file is too large.',
            admin_only: 'Only the server administrator can do this.',
            invalid_date: 'Pick a date between today and race day.',
            b_race_in_past: 'The race must be tomorrow or later.',
            b_race_too_early: 'That date is in the first week of the plan. Pick a later one.',
            b_race_too_late: 'That date falls in the taper or in your goal race week.',
            b_race_too_close: 'Leave at least 2 weeks between tune-up races.',
            race_not_found: 'That race no longer exists.',
            no_race_result: 'There is no valid time for that race.',
            generic: 'Something went wrong. Please try again.',
        },
    },
};

const DISTANCES = ['5k', '10k', '21k', '42k'];
const DISTANCE_KM = { '5k': 5, '10k': 10, '21k': 21.1, '42k': 42.2 };

// First supported language in the browser preferences; English otherwise
function browserLang() {
    const prefs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ''];
    for (const pref of prefs) {
        const code = String(pref).slice(0, 2).toLowerCase();
        if (I18N[code]) return code;
    }
    return 'en';
}

const S = {
    lang: readStorage('gc_lang') || browserLang(),
    me: null,
    garmin: { connected: false },
    pbs: null,  // Garmin records, fetched when the new-plan wizard opens
    profile: null,
    data: null,
    planError: false,  // the last plan fetch failed (not the same as having no plan)
    progress: null,  // Progress tab data; null = not fetched or stale
    progressError: false,
    progressOpen: false,  // "Show details" expanded
    tab: 'today',
    reviewAnswers: { fatigue: null, pain: null },
    openWeeks: new Set(),
    volWeek: null,
};

/* ------------------------------------------------------------- helpers */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function readStorage(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
}

function writeStorage(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode */ }
}

function t(key, vars) {
    const dict = I18N[S.lang] || I18N.es;
    let value = key.split('.').reduce((o, k) => (o == null ? undefined : o[k]), dict);
    if (value === undefined) value = key;
    if (vars && typeof value === 'string') {
        value = value.replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? ''));
    }
    return value;
}

function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

async function api(path, { method = 'GET', body } = {}) {
    let res;
    try {
        res = await fetch(path, {
            method,
            headers: body ? { 'Content-Type': 'application/json' } : undefined,
            body: body ? JSON.stringify(body) : undefined,
        });
    } catch (e) {
        throw new Error('network');
    }
    const data = await res.json().catch(() => ({}));
    if (res.status === 401 && S.me) {
        // Session expired or was deleted: back to the login screen
        S.me = null;
        closeSheet();
        render();
    }
    if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'generic');
    return data;
}

function errText(e) {
    const known = I18N[S.lang].err[e && e.message];
    return known || t('err.generic');
}

function toast(message, kind = 'ok') {
    const el = document.createElement('div');
    el.className = `toast ${kind}`;
    el.textContent = message;
    $('#toasts').appendChild(el);
    setTimeout(() => el.classList.add('hide'), 3200);
    setTimeout(() => el.remove(), 3600);
}

function parseDate(iso) {
    const [y, m, d] = iso.split('-').map(Number);
    return new Date(y, m - 1, d);
}

function isoDate(d) {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function addDays(d, n) {
    const r = new Date(d);
    r.setDate(r.getDate() + n);
    return r;
}

function todayIso() {
    return isoDate(new Date());
}

function fmtDate(iso, opts = { day: 'numeric', month: 'short' }) {
    return parseDate(iso).toLocaleDateString(t('locale'), opts);
}

function relDay(iso) {
    const diff = Math.round((parseDate(iso) - parseDate(todayIso())) / 86400000);
    if (diff === 0) return t('today');
    if (diff === 1) return t('tomorrow');
    if (diff === -1) return t('yesterday');
    return fmtDate(iso, { weekday: 'long', day: 'numeric', month: 'short' });
}

function fmtDuration(sec) {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = Math.round(sec % 60);
    return h ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}` : `${m}:${String(s).padStart(2, '0')}`;
}

function parseDuration(str) {
    if (!/^\d{1,2}(:\d{1,2}){1,2}$/.test((str || '').trim())) return 0;
    const parts = str.trim().split(':').map(Number);
    if (parts.slice(1).some(p => p > 59)) return 0;
    return parts.reduce((acc, p) => acc * 60 + p, 0);
}

// Time field with numeric keypad: the user only types digits and the ":" are inserted
// automatically from the right (5000 → 50:00, 13000 → 1:30:00), keeping the cursor position.
function formatDurationDigits(digits) {
    digits = digits.replace(/\D/g, '').replace(/^0+(?=\d)/, '').slice(0, 6);
    const groups = [];
    for (let end = digits.length; end > 0; end -= 2) groups.unshift(digits.slice(Math.max(0, end - 2), end));
    return groups.join(':');
}

function maskDurationInput(input) {
    const before = input.value.slice(0, input.selectionStart ?? input.value.length).replace(/\D/g, '').length;
    const all = input.value.replace(/\D/g, '');
    const formatted = formatDurationDigits(all);
    input.value = formatted;
    // Digits removed when stripping leading zeros or exceeding 6
    let left = Math.max(0, before - (all.length - formatted.replace(/:/g, '').length)), pos = 0;
    while (pos < formatted.length && left > 0) { if (formatted[pos] !== ':') left -= 1; pos += 1; }
    if (document.activeElement === input) input.setSelectionRange(pos, pos);
}

function nextMonday() {
    const d = new Date();
    const offset = (8 - d.getDay()) % 7 || 7;
    return addDays(new Date(d.getFullYear(), d.getMonth(), d.getDate()), offset);
}

/* --------------------------------------------------------------- sheet */

function openSheet(title, html, onMount) {
    const panel = $('.sheet-panel');
    panel.style.transform = '';
    panel.classList.remove('settle', 'dragging');
    // A new sheet starts at the top; re-rendering the same one (e.g. a wizard step) keeps the scroll
    const fresh = $('#sheet').hidden || $('#sheetTitle').textContent !== title;
    $('#sheetTitle').textContent = title;
    const body = $('#sheetBody');
    // Delegated handlers from the previous sheet (wizard, settings) must not survive
    body.onclick = body.oninput = body.onchange = null;
    body.innerHTML = html;
    $('#sheet').hidden = false;
    if (fresh) panel.scrollTop = 0;
    document.body.classList.add('no-scroll');
    if (onMount) onMount($('#sheetBody'));
}

function closeSheet() {
    $('#sheet').hidden = true;
    $('#sheetBody').innerHTML = '';
    document.body.classList.remove('no-scroll');
}

function confirmSheet(title, message, okLabel, onOk) {
    openSheet(title, `
        <p class="muted">${esc(message)}</p>
        <div class="actions">
            <button type="button" class="btn ghost" data-close>${t('cancel')}</button>
            <button type="button" class="btn danger" id="confirmOk">${esc(okLabel)}</button>
        </div>`, body => {
        $('#confirmOk', body).onclick = async e => {
            e.target.disabled = true;
            await onOk();
        };
    });
}

/* -------------------------------------------------------------- loading */

async function loadAll() {
    try {
        S.me = await api('/api/me');
    } catch (e) {
        S.me = null;
        render();
        return;
    }
    setLang(S.me.language, false);
    const [garmin, profile] = await Promise.allSettled([
        api('/api/garmin/status'), api('/api/profile'), fetchPlan(),
    ]);
    if (garmin.status === 'fulfilled') S.garmin = garmin.value;
    if (profile.status === 'fulfilled') {
        S.profile = profile.value;
        setLang(S.profile.language, false);
    }
    render();
}

const PLAN_RETRY_MS = [1000, 3000];

async function fetchPlan() {
    // A failed plan fetch must not show as "no plan" (it would invite creating another one
    // and cancelling the current one): retry, and if it keeps failing, keep the last loaded data.
    for (let attempt = 0; ; attempt++) {
        try {
            S.data = await api('/api/plans/active');
            S.planError = false;
            Object.assign(S, { progress: null, progressError: false });
            return;
        } catch (e) {
            if (!S.me) return;  // session expired: api() already went to the login screen
            if (attempt >= PLAN_RETRY_MS.length) {
                S.planError = true;
                return;
            }
            await new Promise(r => setTimeout(r, PLAN_RETRY_MS[attempt]));
        }
    }
}

async function reloadPlan() {
    await fetchPlan();
    if (S.planError && S.data && S.data.active) toast(t('err.generic'), 'error');
    render();
}

function setLang(lang, rerender = true) {
    S.lang = I18N[lang] ? lang : browserLang();
    document.documentElement.lang = S.lang;
    writeStorage('gc_lang', S.lang);
    if (rerender) render();
}

/* ------------------------------------------------------------- rendering */

const TAB_TITLES = { today: 'tabToday', plan: 'tabPlan', progress: 'tabProgress' };

function render() {
    renderTopbar();
    const view = $('#view');
    if (!S.me) {
        $('#tabs').hidden = true;
        $('#smallTitle').textContent = '';
        view.innerHTML = renderLogin();
        bindConnect(view);
        return;
    }
    const hasPlan = S.data && S.data.active;
    $('#tabs').hidden = !hasPlan;
    if (!hasPlan) {
        $('#smallTitle').textContent = '';
        view.innerHTML = S.planError ? renderLoadError() : renderEmpty();
    } else {
        const tabs = { plan: renderPlanTab, progress: renderProgressTab };
        const title = t(TAB_TITLES[S.tab] || 'tabToday');
        $('#smallTitle').textContent = title;
        view.innerHTML = `<h1 class="large-title">${esc(title)}</h1>${(tabs[S.tab] || renderToday)()}`;
    }
}

function renderTopbar() {
    // Profile button: name initial and Garmin status dot; opens Settings
    const btn = $('#profileBtn');
    btn.hidden = !S.me;
    const help = $('#helpBtn');
    help.hidden = !S.me;
    help.setAttribute('aria-label', t('helpOpen'));
    help.title = t('helpOpen');
    if (S.me) {
        const name = (S.me.name || 'Garmin').trim();
        $('#profileInitial').textContent = (name[0] || 'G').toUpperCase();
        btn.classList.toggle('on', !!S.garmin.connected);
        const status = S.garmin.connected ? t('connected') : t('notConnected');
        btn.setAttribute('aria-label', `${t('settings')} · ${name} · ${status}`);
        btn.title = `${name} · ${status}`;
    }
    $('.sheet-title-row [data-close]').setAttribute('aria-label', t('close'));
    $$('#tabs .tab').forEach(b => {
        $('.tab-label', b).textContent = t(TAB_TITLES[b.dataset.tab]);
        b.setAttribute('aria-selected', String(b.dataset.tab === S.tab));
    });
}

function connectBanner() {
    if (S.garmin.connected) return '';
    return `<div class="banner warn">
        <p>${t('garminExpired')}</p>
        <button type="button" class="btn small" data-action="connect">${t('reconnect')}</button>
    </div>`;
}

function renderLogin() {
    return `
        <section class="empty login">
            <img src="/static/icon-192.png" alt="" width="72" height="72">
            <h1>${t('loginTitle')}</h1>
            <p class="muted">${t('loginText')}</p>
            <div class="card login-card">${connectFormHtml()}</div>
        </section>`;
}

function renderEmpty() {
    return `
        <section class="empty">
            <img src="/static/icon-192.png" alt="" width="72" height="72">
            <h1>${t('emptyTitle')}</h1>
            <p class="muted">${t('emptyText')}</p>
            <button type="button" class="btn primary big" data-action="new-plan">${t('createPlan')}</button>
            <button type="button" class="btn ghost" data-action="history">${t('historyOpen')}</button>
        </section>
        ${connectBanner()}`;
}

function renderLoadError() {
    return `
        <section class="empty">
            <img src="/static/icon-192.png" alt="" width="72" height="72">
            <h1>${t('loadErrorTitle')}</h1>
            <p class="muted">${t('loadErrorText')}</p>
            <button type="button" class="btn primary big" data-action="reload">${t('retry')}</button>
        </section>`;
}

function typeTag(type) {
    return `<span class="tag t-${esc(type)}">${esc(t(`type.${type}`))}</span>`;
}

function statusIcon(status) {
    if (status === 'completed') return '<span class="st st-done" aria-hidden="true">✓</span>';
    if (status === 'missed') return '<span class="st st-missed" aria-hidden="true">–</span>';
    return '<span class="st st-todo" aria-hidden="true"></span>';
}

function paceLevelKey(level, direction) {
    return level === 'ok' ? 'ok' : `${level}_${direction}`;
}

function paceIcon(level, direction) {
    if (level === 'ok') return '✓';
    return direction === 'fast' ? '▲' : '▼';
}

function paceFlag(w) {
    if (w.status !== 'completed' || !w.pace || w.pace === 'ok') return '';
    return `<span class="pace-flag p-${esc(w.pace)}">${paceIcon(w.pace, w.pace_dir)} ${esc(t(`paceLevel.${paceLevelKey(w.pace, w.pace_dir)}`))}</span>`;
}

function workoutRow(w) {
    const d = parseDate(w.date);
    const dayIdx = (d.getDay() + 6) % 7;
    const isToday = w.date === todayIso();
    return `
        <button type="button" class="row ${w.status} ${isToday ? 'is-today' : ''}" data-workout="${w.id}">
            <span class="row-date"><b>${t('daysShort')[dayIdx]}</b><small>${d.getDate()}</small></span>
            <span class="row-main">
                <span class="row-title">${esc(w.title)}</span>
                <span class="row-meta">${typeTag(w.type)} ${w.distance_km ?? '–'} km · ~${w.duration_min ?? '–'} min${w.on_watch ? ' · <span class="watch">⌚</span>' : ''}${paceFlag(w)}</span>
            </span>
            ${statusIcon(w.status)}
        </button>`;
}

function renderToday() {
    const { plan, prediction, stats, next_workout: nw, weeks, sync } = S.data;
    const week = weeks.find(w => w.is_current) || weeks[0];
    const progress = stats.sessions_total ? Math.round(100 * stats.sessions_done / stats.sessions_total) : 0;
    const countdown = plan.days_to_race === 0
        ? `<div class="countdown"><b>${t('raceDay')}</b></div>`
        : `<div class="countdown"><b>${plan.days_to_race}</b><span>${t('daysToRace')}</span></div>`;

    let syncNote = '';
    if (sync.connected && sync.syncing) {
        syncNote = `<div class="banner"><p><span class="spinner inline"></span> ${t('syncing')}</p></div>`;
    } else if (sync.connected && sync.pending > 0 && (sync.failed || sync.pending_soon > 0)) {
        syncNote = `<div class="banner warn"><p>${t('pendingSync', { n: sync.pending })}</p>
            <button type="button" class="btn small" data-action="sync">${t('retry')}</button></div>`;
    }
    watchSync(sync.syncing);

    return `
        ${connectBanner()}
        ${syncNote}
        <div class="grid">
            ${reviewCard()}
            ${raceProposalCard()}
            ${rpeCard()}
            <section class="card hero">
                <div class="hero-top">
                    <div>
                        <p class="eyebrow">${esc(plan.name)}</p>
                        ${countdown}
                    </div>
                    <div class="hero-pred">
                        <span class="eyebrow">${t('prediction')}</span>
                        <b>${esc(prediction.formatted_nominal)}</b>
                        <small>${esc(prediction.formatted_pace)}</small>
                    </div>
                </div>
                <div class="progress"><span style="width:${progress}%"></span></div>
                <div class="hero-foot">
                    <span>${t('weekOf', { w: plan.current_week, n: plan.total_weeks })} · ${esc(t(`phase.${week.phase}`))}</span>
                    <span>${t('sessionsDone', { d: stats.sessions_done, n: stats.sessions_total })}</span>
                </div>
            </section>

            <section class="card next">
                <p class="eyebrow">${t('nextWorkout')}</p>
                ${nw ? nextWorkoutCard(nw, sync) : `<p class="muted">${t('noUpcoming')}</p>`}
            </section>

            <section class="card">
                <div class="card-head">
                    <h2>${t('thisWeek')}</h2>
                    <span class="muted small">${realKm(week)} / ${week.planned_km} km</span>
                </div>
                <div class="rows">${week.workouts.map(workoutRow).join('')}</div>
            </section>

        </div>`;
}

function meter(label, pct, detail) {
    const width = pct == null ? 0 : Math.min(100, pct);
    return `<div class="meter">
        <span class="meter-label">${esc(label)}</span>
        <b>${pct == null ? '–' : pct + '%'}</b>
        <span class="meter-bar"><span style="width:${width}%"></span></span>
        <small>${esc(detail)}</small>
    </div>`;
}

function adherenceCard(a) {
    const head = `<div class="card-head"><h2>${t('compliance')}</h2></div>`;
    if (!a || !a.sessions.total) {
        return `<section class="card wide adh">${head}<p class="muted small">${t('adhEmpty')}</p></section>`;
    }
    const p = a.pace;
    const byType = a.by_type.map(x => `
        <div class="bt-row">
            ${typeTag(x.type)}
            <span class="meter-bar"><span style="width:${x.pct}%"></span></span>
            <small>${x.done}/${x.total}</small>
        </div>`).join('');
    return `<section class="card wide adh">
        ${head}
        <div class="meters">
            ${meter(t('adhSessions'), a.sessions.pct, t('adhOf', { d: a.sessions.done, n: a.sessions.total }))}
            ${meter(t('adhKm'), a.km.pct, t('adhKmOf', { d: a.km.done, n: a.km.planned }))}
            ${meter(t('adhPace'), p.pct, p.checked ? t('adhPaceDetail', p) : t('adhNoPace'))}
        </div>
        <p class="eyebrow bt-title">${t('byType')}</p>
        <div class="by-type">${byType}</div>
    </section>`;
}

function fmtVdot(v) {
    return Number(v).toLocaleString(t('locale'), { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

// Fitness chart X axis: from plan start to today
function formX(iso) {
    const start = parseDate(S.data.plan.start_date);
    const span = Math.max(1, (parseDate(todayIso()) - start) / 86400000);
    return 100 * (parseDate(iso) - start) / 86400000 / span;
}

function formPlanVdotAt(iso) {
    const steps = S.progress.form.history;
    let v = steps[0].vdot;
    for (const s of steps) if (s.date <= iso) v = s.vdot;
    return v;
}

function formChart(f) {
    if (todayIso() <= S.data.plan.start_date) return `<p class="muted small">${t('formNotStarted')}</p>`;
    const values = [...f.history.map(h => h.vdot), ...f.sessions.map(s => s.vdot)];
    const lo = Math.floor(Math.min(...values) - 1);
    const hi = Math.ceil(Math.max(...values) + 1);
    const y = v => 100 * (1 - (v - lo) / (hi - lo));
    // Steps: each value holds until the next change and extends to today
    const pts = [];
    f.history.forEach((h, i) => {
        const x0 = Math.max(0, formX(h.date));
        const next = f.history[i + 1];
        const x1 = next ? Math.max(0, formX(next.date)) : 100;
        pts.push(`${x0.toFixed(2)},${y(h.vdot).toFixed(2)}`, `${x1.toFixed(2)},${y(h.vdot).toFixed(2)}`);
    });
    const ticks = [lo, Math.round((lo + hi) / 2), hi];
    const dots = f.sessions.map(s => `<span class="fdot" style="left:${formX(s.date)}%;top:${y(s.vdot)}%"></span>`).join('');
    return `
        <div class="lchart fchart" data-chart="form">
            <div class="laxis">${ticks.map(v => `<span style="top:${y(v)}%">${v}</span>`).join('')}</div>
            <div class="lplot">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                    <polyline class="lline" points="${pts.join(' ')}"/>
                </svg>
                ${dots}
                <span class="lcross" hidden></span>
            </div>
        </div>
        <div class="vlegend">
            <span><i class="key-line"></i>${t('formLegendPlan')}</span>
            <span><i class="key-dot"></i>${t('formLegendSession')}</span>
        </div>
        <p class="lreadout muted small" id="formReadout">${t('formChartHint')}</p>`;
}

// Date under the cursor; if a workout is nearby, show that one
function formPoint(pct) {
    const start = parseDate(S.data.plan.start_date);
    const days = Math.round(pct / 100 * (parseDate(todayIso()) - start) / 86400000);
    let iso = isoDate(addDays(start, days));
    const near = S.progress.form.sessions.find(s => Math.abs(formX(s.date) - pct) < 2.5);
    if (near) iso = near.date;
    let text = `${fmtDate(iso)} · ${t('formLegendPlan')} ${fmtVdot(formPlanVdotAt(iso))}`;
    if (near) text += ` · ${t(`type.${near.type}`)} ${fmtVdot(near.vdot)}`;
    return { x: formX(iso), text };
}

function predictionsTable(f) {
    const withForm = !!f.estimate;
    const rows = f.predictions.map(p => `
        <tr class="${p.is_target ? 'target' : ''}">
            <th scope="row">${esc(p.distance.toUpperCase())}${p.is_target ? ` <span class="muted small">${t('predTarget')}</span>` : ''}</th>
            <td>${esc(p.plan)}</td>
            ${withForm ? `<td>${esc(p.form)}</td>` : ''}
        </tr>`).join('');
    return `
        <h3 class="sub">${t('predTitle')}</h3>
        <table class="pred">
            <thead><tr><th scope="col">${t('predDistance')}</th><th scope="col">${t('predPlan')}</th>${withForm ? `<th scope="col">${t('predForm')}</th>` : ''}</tr></thead>
            <tbody>${rows}</tbody>
        </table>
        <p class="muted small">${t('predNote')}</p>`;
}

function formCard(f) {
    const est = f.estimate;
    const vo2 = S.progress.vo2max;
    let summary = '';
    if (est) {
        const d = Math.round((est.vdot - f.vdot) * 10) / 10;
        summary = Math.abs(d) < 1 ? t('formSame')
            : `${t(d > 0 ? 'formAbove' : 'formBelow', { f: fmtVdot(est.vdot), d: fmtVdot(Math.abs(d)) })} ${t('formGradual')}`;
    }
    return `<section class="card wide form">
        <div class="card-head"><h2>${t('formTitle')}</h2></div>
        <div class="figures">
            <div class="figure"><span>${t('formPlan')}</span><b>${fmtVdot(f.vdot)}</b></div>
            <div class="figure"><span>${t('formEstimate')}</span><b>${est ? fmtVdot(est.vdot) : '–'}</b>
                <small>${est ? t('formSessions', { n: est.sessions }) : t('formNeeds')}</small></div>
            ${vo2 ? `<div class="figure"><span>${t('formGarmin')}</span><b>${fmtVdot(vo2)}</b></div>` : ''}
        </div>
        ${summary ? `<p class="small form-summary">${esc(summary)}</p>` : ''}
        ${formChart(f)}
        ${predictionsTable(f)}
        ${vo2 ? `<p class="about">${t('garminNote')}</p>` : ''}
    </section>`;
}

function fmtEff(v) {
    return Number(v).toLocaleString(t('locale'), { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function effX(iso) {
    const s = S.progress.efficiency.series;
    const first = parseDate(s[0].date);
    const span = Math.max(1, (parseDate(s[s.length - 1].date) - first) / 86400000);
    return 100 * (parseDate(iso) - first) / 86400000 / span;
}

function efficiencyChart(series) {
    const values = series.map(p => p.value);
    const lo = Math.min(...values) * 0.97;
    const hi = Math.max(...values) * 1.03;
    const y = v => 100 * (1 - (v - lo) / (hi - lo));
    const line = series.map(p => `${effX(p.date).toFixed(2)},${y(p.trend).toFixed(2)}`).join(' ');
    const dots = series.map(p => `<span class="fdot" style="left:${effX(p.date)}%;top:${y(p.value)}%"></span>`).join('');
    const ticks = [lo, (lo + hi) / 2, hi];
    return `
        <div class="lchart fchart" data-chart="eff">
            <div class="laxis">${ticks.map(v => `<span style="top:${y(v)}%">${fmtEff(v)}</span>`).join('')}</div>
            <div class="lplot">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><polyline class="lline" points="${line}"/></svg>
                ${dots}
                <span class="lcross" hidden></span>
            </div>
        </div>
        <div class="vlegend">
            <span><i class="key-dot"></i>${t('effLegendRun')}</span>
            <span><i class="key-line"></i>${t('effLegendTrend')}</span>
        </div>
        <p class="lreadout muted small" id="effReadout">&nbsp;</p>`;
}

function effPoint(pct) {
    const p = nearestPoint(S.progress.efficiency.series, effX, pct);
    return { x: effX(p.date), text: `${fmtDate(p.date)} · ${fmtEff(p.value)} ${t('effUnit')} · ${t('effLegendTrend')} ${fmtEff(p.trend)}` };
}

function intensityBlock(m) {
    if (m.easy_pct == null) return `<p class="muted small">${t('mixEmpty')}</p>`;
    const parts = [['easy', m.easy_pct, 'mixEasy'], ['moderate', m.moderate_pct, 'mixModerate'], ['hard', m.hard_pct, 'mixHard']];
    const bar = parts.filter(p => p[1] > 0).map(([k, v, label]) =>
        `<span class="mix-${k}" style="flex-grow:${v}" title="${esc(t(label))} ${v}%"></span>`).join('');
    const legend = parts.map(([k, v, label]) => `<span><i class="sw mix-${k}"></i>${t(label)} <b>${v}%</b></span>`).join('');
    const verdict = m.balanced
        ? `<p class="small mix-verdict ok">${t('mixOk', { pct: m.easy_pct })}</p>`
        : `<p class="small mix-verdict warn">${t('mixHigh', { pct: m.easy_pct })}</p>`;
    return `
        <div class="mixbar" role="img" aria-label="${esc(parts.map(([, v, l]) => `${t(l)} ${v}%`).join(', '))}">${bar}</div>
        <div class="vlegend mix-legend">${legend}</div>
        ${verdict}
        ${m.moderate_pct >= 10 ? `<p class="muted small">${t('mixGrey', { pct: m.moderate_pct })}</p>` : ''}
        <p class="muted small">${t('mixMinutes', { n: m.minutes })}</p>`;
}

function aerobicCard(eff, mix) {
    let effBlock;
    if (eff.series.length < 4) {
        effBlock = `<p class="muted small">${t('effNeeds')}</p>`;
    } else {
        const c = eff.change_pct;
        const change = Math.abs(c) < 1 ? t('effFlat') : t(c > 0 ? 'effUp' : 'effDown', { pct: fmtVdot(Math.abs(c)) });
        effBlock = `
            <div class="figures">
                <div class="figure"><span>${t('effLabel')}</span><b>${fmtEff(eff.latest)}</b><small>${esc(change)}</small></div>
            </div>
            ${efficiencyChart(eff.series)}`;
    }
    return `<section class="card wide aero">
        <div class="card-head"><h2>${t('aeroTitle')}</h2></div>
        <h3 class="sub first">${t('effTitle')}</h3>
        ${effBlock}
        <p class="about">${t('effHint')}</p>
        <h3 class="sub">${t('mixTitle')}</h3>
        ${intensityBlock(mix)}
    </section>`;
}

// Progress is fetched when the tab opens (the most expensive thing to compute on the NAS); S.progress
// is discarded when the plan changes and fetched again the next time it is shown
let progressLoading = false;

async function loadProgress() {
    if (progressLoading) return;
    progressLoading = true;
    try {
        S.progress = await api('/api/plans/active/progress');
        S.progressError = false;
    } catch (e) {
        S.progressError = true;
    } finally {
        progressLoading = false;
    }
    if (S.tab === 'progress' && S.me) render();
}

// Plain-language summary: fitness, race prediction, compliance and load
function overviewCard(p) {
    const est = p.form.estimate;
    const a = p.adherence.sessions;
    const load = p.load;
    const pred = S.data.prediction;
    const loadText = load.ratio == null ? t('sumLoadBuilding') : `${LOAD_ICON[load.zone]} ${t(`loadZone.${load.zone}`)}`;
    return `<section class="card wide">
        <div class="overview">
            <div class="figure"><span>${t('sumForm')}</span><b>${fmtVdot(p.form.vdot)}</b>
                <small>${est ? t('sumFormEst', { v: fmtVdot(est.vdot) }) : t('sumFormPlan')}</small></div>
            <div class="figure"><span>${t('sumRace', { d: S.data.plan.target_distance.toUpperCase() })}</span>
                <b>${esc(pred.formatted_nominal)}</b><small>${esc(pred.formatted_pace)}</small></div>
            <div class="figure"><span>${t('compliance')}</span><b>${a.pct == null ? '–' : `${a.pct}%`}</b>
                <small>${a.total ? t('adhOf', { d: a.done, n: a.total }) : t('adhEmpty')}</small></div>
            <div class="figure"><span>${t('sumLoad')}</span><b class="word zone z-${esc(load.zone || '')}">${esc(loadText)}</b></div>
        </div>
        <p class="about">${t('formWhat')}</p>
    </section>`;
}

function renderProgressTab() {
    if (!S.progress) {
        if (S.progressError) {
            return `<section class="empty"><p class="muted">${t('progressError')}</p>
                <button type="button" class="btn primary" data-action="reload-progress">${t('retry')}</button></section>`;
        }
        loadProgress();
        return '<div class="loading"><span class="spinner"></span></div>';
    }
    const p = S.progress;
    return `<div class="grid">${overviewCard(p)}</div>
        <details class="more" id="progressMore" ${S.progressOpen ? 'open' : ''}>
            <summary>${t('seeDetail')}</summary>
            <div class="grid">
                ${formCard(p.form)}
                ${aerobicCard(p.efficiency, p.intensity)}
                ${loadCard(p.load)}
                ${adherenceCard(p.adherence)}
            </div>
        </details>`;
}

// The detail block remembers whether it was open across re-renders ("toggle" does not bubble)
document.addEventListener('toggle', e => {
    if (e.target.id === 'progressMore') S.progressOpen = e.target.open;
}, true);

const LOAD_ICON = { low: '▼', optimal: '✓', caution: '▲', high: '▲' };
const LOAD_BAND = [0.8, 1.3];

function fmtRatio(v) {
    return Number(v).toLocaleString(t('locale'), { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Horizontal position (%) of a date: the axis runs from the first data point (max. 8 weeks back) to today
function loadX(iso) {
    const series = S.progress.load.series;
    const end = parseDate(todayIso());
    const span = Math.max(1, (end - parseDate(series[0].date)) / 86400000);
    return 100 * (1 - (end - parseDate(iso)) / 86400000 / span);
}

function loadChart(series) {
    if (series.length < 2) return '';
    const yMin = 0.4;
    const yMax = Math.max(1.8, ...series.map(p => p.ratio)) + 0.1;
    const y = v => 100 * (1 - (Math.min(Math.max(v, yMin), yMax) - yMin) / (yMax - yMin));
    const pts = series.map(p => `${loadX(p.date).toFixed(2)},${y(p.ratio).toFixed(2)}`).join(' ');
    const last = series[series.length - 1];
    const labels = LOAD_BAND.map(v => `<span style="top:${y(v)}%">${fmtRatio(v)}</span>`).join('');
    return `
        <div class="lchart" data-chart="load">
            <div class="laxis">${labels}</div>
            <div class="lplot">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                    <rect class="lband" x="0" width="100" y="${y(LOAD_BAND[1])}" height="${y(LOAD_BAND[0]) - y(LOAD_BAND[1])}"/>
                    <polyline class="lline" points="${pts}"/>
                </svg>
                <span class="lcross" hidden></span>
                <span class="ldot" style="left:${loadX(last.date)}%;top:${y(last.ratio)}%"></span>
            </div>
        </div>
        <p class="lreadout muted small" id="loadReadout">${t('loadChart', { d: fmtDate(series[0].date) })}</p>`;
}

function loadCard(l) {
    if (!l) return '';
    const head = `<div class="card-head"><h2>${t('loadTitle')}</h2></div>`;
    if (l.ratio == null) {
        return `<section class="card wide load">${head}
            <p class="muted small">${t('loadBuilding', { n: l.available_in_days || 1 })}</p>
            <p class="about">${t('loadAbout')}</p>
        </section>`;
    }
    const pct = Math.round((l.ratio - 1) * 100);
    const vs = Math.abs(pct) < 3 ? t('loadVs.same') : t(pct > 0 ? 'loadVs.up' : 'loadVs.down', { pct: Math.abs(pct) });
    const advice = l.zone === 'optimal' ? '' : `<p class="small">${esc(t(`loadAdvice.${l.zone}`))}</p>`;
    return `<section class="card wide load">
        ${head}
        <div class="load-top">
            <div class="load-figure">
                <b>${fmtRatio(l.ratio)}</b>
                <span class="zone z-${esc(l.zone)}">${LOAD_ICON[l.zone]} ${esc(t(`loadZone.${l.zone}`))}</span>
            </div>
            <div class="load-text"><p class="muted small">${esc(vs)}</p>${advice}</div>
        </div>
        ${loadChart(l.series)}
        <p class="about">${t('loadAbout')}</p>
    </section>`;
}

function loadPoint(pct) {
    const p = nearestPoint(S.progress.load.series, loadX, pct);
    return { x: loadX(p.date), text: `${fmtDate(p.date)} · ${fmtRatio(p.ratio)}` };
}

// Charts with a readout on hover or touch: the point under the finger, with its date and value.
// at(pct) returns the vertical line position and the text; idle() is the resting text.
const CHARTS = {
    form: { readout: '#formReadout', at: formPoint, idle: () => t('formChartHint') },
    eff: { readout: '#effReadout', at: effPoint, idle: () => String.fromCharCode(160) },
    load: { readout: '#loadReadout', at: loadPoint, idle: () => t('loadChart', { d: fmtDate(S.progress.load.series[0].date) }) },
};

function nearestPoint(series, xOf, pct) {
    return series.reduce((a, b) => (Math.abs(xOf(b.date) - pct) < Math.abs(xOf(a.date) - pct) ? b : a));
}

function chartHover(e) {
    const chart = e.target.closest && e.target.closest('[data-chart]');
    if (!chart) return;
    const plot = $('.lplot', chart).getBoundingClientRect();
    const pct = 100 * Math.min(1, Math.max(0, (e.clientX - plot.left) / plot.width));
    const { x, text } = CHARTS[chart.dataset.chart].at(pct);
    const cross = $('.lcross', chart);
    cross.hidden = false;
    cross.style.left = `${x}%`;
    $(CHARTS[chart.dataset.chart].readout).textContent = text;
}

function chartHoverEnd(e) {
    const chart = e.target.closest && e.target.closest('[data-chart]');
    if (!chart || (e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest('[data-chart]') === chart)) return;
    $('.lcross', chart).hidden = true;
    $(CHARTS[chart.dataset.chart].readout).textContent = CHARTS[chart.dataset.chart].idle();
}

document.addEventListener('pointermove', chartHover);
document.addEventListener('pointerdown', chartHover);
document.addEventListener('pointerout', chartHoverEnd);

// While the server uploads workouts to the watch, poll the status every few seconds
let syncPoll = null;
function watchSync(syncing) {
    if (!syncing || syncPoll) return;
    let tries = 0;
    syncPoll = setInterval(async () => {
        tries += 1;
        try {
            const data = await api('/api/plans/active');
            if (!data.active || !data.sync.syncing || tries > 40) {
                clearInterval(syncPoll);
                syncPoll = null;
                S.data = data;
                if ($('#sheet').hidden) render();
            }
        } catch (e) {
            clearInterval(syncPoll);
            syncPoll = null;
        }
    }, 3000);
}

const RPE_VALUES = [3, 5, 7, 9];

function rpeChips(workoutId, current) {
    return `<div class="chips">${RPE_VALUES.map(v => `<button type="button" class="chip ${current === v ? 'on' : ''}" data-rpe="${v}" data-rpe-workout="${workoutId}">${esc(t(`rpeOpt.${v}`))}</button>`).join('')}</div>`;
}

function rpeCard() {
    const w = S.data.rpe_prompt;
    if (!w) return '';
    return `<section class="card wide ask">
        <p class="ask-title">${esc(t('rpeQuestion', { title: w.title }))}</p>
        ${rpeChips(w.id, null)}
    </section>`;
}

function reviewCard() {
    const r = S.data.review;
    if (!r) return '';
    const title = r.week_from === r.week_to ? t('reviewTitleOne', { a: r.week_from }) : t('reviewTitle', { a: r.week_from, b: r.week_to });
    const m = r.metrics;
    const metrics = `<p class="muted small">${t('reviewMetrics', { c: m.completed, p: m.planned, kd: m.km_done, kp: m.km_planned })}</p>`;

    if (r.stage === 'questions') {
        const a = S.reviewAnswers;
        const ready = a.fatigue && a.pain;
        return `<section class="card wide review">
            <p class="eyebrow">${esc(title)}</p>
            ${metrics}
            <div class="field"><span>${t('qFatigue')}</span>${chips('rfatigue', ['good', 'tired', 'very_tired'], a.fatigue, o => t(`fatigueOpt.${o}`))}</div>
            <div class="field"><span>${t('qPain')}</span>${chips('rpain', ['no', 'mild', 'yes'], a.pain, o => t(`painOpt.${o}`))}</div>
            <div class="actions spread">
                <button type="button" class="btn ghost small" data-action="review-skip">${t('skip')}</button>
                <button type="button" class="btn primary small" data-action="review-submit" ${ready ? '' : 'disabled'}>${t('seeProposal')}</button>
            </div>
        </section>`;
    }

    const p = r.proposal;
    const vars = x => (x.ratio != null ? { ...x, ratio: fmtRatio(x.ratio) } : x);
    const reasons = p.reasons.map(x => `<li>${esc(t(`reason.${x.code}`, vars(x)))}</li>`).join('');
    const tips = p.tips.map(x => `<li class="tip">${esc(t(`tip.${x.code}`, vars(x)))}</li>`).join('');
    const changes = [];
    if (p.vdot_to !== p.vdot_from) changes.push(t('chVdot', { a: p.vdot_from, b: p.vdot_to, pa: p.prediction_from, pb: p.prediction_to }));
    if (p.volume_to !== p.volume_from) changes.push(t('chVolume', { pct: Math.round(p.volume_to * 100) }));
    if (p.deload_week) changes.push(t('chDeload'));
    const actions = p.changes
        ? `<button type="button" class="btn ghost small" data-action="review-decline" data-review="${r.id}">${t('keepPlan')}</button>
           <button type="button" class="btn primary small" data-action="review-accept" data-review="${r.id}">${t('accept')}</button>`
        : `<span></span><button type="button" class="btn primary small" data-action="review-accept" data-review="${r.id}">${t('gotIt')}</button>`;
    return `<section class="card wide review">
        <p class="eyebrow">${esc(title)}</p>
        <h2>${t('proposalTitle')}</h2>
        <ul class="reasons">${reasons}${tips}</ul>
        ${changes.length ? `<ul class="changes">${changes.map(c => `<li>${esc(c)}</li>`).join('')}</ul>` : ''}
        <div class="actions spread">${actions}</div>
    </section>`;
}

function raceLabel(r) {
    return r.name || `${t('type.race')} ${r.distance.toUpperCase()}`;
}

function raceProposalCard() {
    const r = S.data.race_proposal;
    if (!r) return '';
    return `<section class="card wide review">
        <p class="eyebrow">${t('raceProposalTitle')}</p>
        <p>${esc(t('raceProposalText', { name: raceLabel(r), t: fmtDuration(r.result.time_sec), a: r.vdot_from, b: r.vdot_to }))}</p>
        <p class="muted small">${t('raceProposalAsk')}</p>
        <div class="actions spread">
            <button type="button" class="btn ghost small" data-action="race-vdot-dismiss" data-race="${r.id}">${t('keepPlan')}</button>
            <button type="button" class="btn primary small" data-action="race-vdot-accept" data-race="${r.id}">${t('updatePaces')}</button>
        </div>
    </section>`;
}

function racesCard(races) {
    const today = todayIso();
    const rows = races.map(r => `
        <div class="race-row">
            <span>
                <b>${esc(raceLabel(r))}</b>
                <small class="muted">${esc(fmtDate(r.date, { weekday: 'short', day: 'numeric', month: 'short' }))} · ${esc(r.distance.toUpperCase())}${r.result ? ` · ${esc(t('raceResult', { t: fmtDuration(r.result.time_sec) }))}` : ''}</small>
            </span>
            ${r.date > today ? `<button type="button" class="btn ghost small danger-text" data-action="race-delete" data-race="${r.id}" aria-label="${esc(t('raceDelete'))}">✕</button>` : ''}
        </div>`).join('');
    return `<section class="card races">
        <div class="card-head"><h2>${t('races')}</h2></div>
        ${rows ? `<div class="race-rows">${rows}</div>` : ''}
        <div class="set-row">
            <p class="hint">${t('racesHint')}</p>
            <button type="button" class="btn ghost small" data-action="race-add">${t('raceAdd')}</button>
        </div>
    </section>`;
}

function openAddRace() {
    let distance = '10k';
    const min = isoDate(addDays(new Date(), 1));
    openSheet(t('raceAdd'), `
        <label class="field"><span>${t('eventName')}</span><input type="text" id="rName" maxlength="80" placeholder="${esc(t('raceNameHint'))}" autocomplete="off"></label>
        <div class="field"><span>${t('distance')}</span>${chips('rdist', B_DISTANCES, distance, d => d.toUpperCase())}</div>
        <label class="field"><span>${t('raceDate')}</span><input type="date" id="rDate" min="${min}" max="${S.data.plan.target_date}"></label>
        <p class="hint">${t('raceAddHint')}</p>
        <div class="actions">
            <button type="button" class="btn ghost" data-close>${t('cancel')}</button>
            <button type="button" class="btn primary" id="rSave" disabled>${t('save')}</button>
        </div>`, body => {
        const date = $('#rDate', body), save = $('#rSave', body);
        const distChips = [...body.querySelectorAll('[data-rdist]')];
        distChips.forEach(c => {
            c.onclick = () => {
                distance = c.dataset.rdist;
                distChips.forEach(o => {
                    o.classList.toggle('on', o === c);
                    o.setAttribute('aria-pressed', o === c);
                });
            };
        });
        date.oninput = () => { save.disabled = !date.value; };
        save.onclick = async () => {
            save.disabled = true;
            try {
                await api('/api/plans/active/races', {
                    method: 'POST', body: { race_date: date.value, distance, name: $('#rName', body).value },
                });
                closeSheet();
                toast(t('raceAdded'));
                await reloadPlan();
            } catch (err) { toast(errText(err), 'error'); save.disabled = false; }
        };
    });
}

function nextWorkoutCard(w, sync) {
    let watch;
    if (w.on_watch) watch = `<span class="watch-ok">⌚ ${t('onWatch')}</span>`;
    else if (!sync.connected) watch = `<span class="muted">${t('notConnected')}</span>`;
    else watch = `<span class="muted">${t('willSync')}</span>`;
    const steps = (w.steps || []).filter(s => s.kind !== 'recovery');
    const shown = steps.slice(0, 4);
    return `
        <button type="button" class="next-body" data-workout="${w.id}">
            <span class="next-when">${esc(relDay(w.date))}</span>
            <span class="next-title">${esc(w.title)}</span>
            <span class="next-meta">${typeTag(w.type)} ${w.distance_km} km · ~${w.duration_min} min</span>
            <span class="mini-steps">${shown.map(s => `<span><b>${esc(s.label)}</b> ${esc(s.duration)}${s.pace ? ` · ${esc(s.pace)}` : ''}</span>`).join('')}${steps.length > shown.length ? '<span>…</span>' : ''}</span>
        </button>
        <div class="next-foot">${watch}</div>`;
}

const LIGHT_PHASES = ['deload', 'tuneup', 'taper'];
const B_DISTANCES = ['5k', '10k', '21k'];

function realKm(w) {
    return Math.round(10 * (w.done_km + (w.extra_km || 0))) / 10;
}

function niceStep(max) {
    return [5, 10, 20, 25, 50].find(step => max / step <= 4) || 100;
}

function weekStarted(w) {
    return w.week_number <= S.data.plan.current_week;
}

function weekRange(n) {
    const start = parseDate(S.data.plan.start_date);
    const monday = addDays(start, -((start.getDay() + 6) % 7) + 7 * (n - 1));
    const sunday = addDays(monday, 6);
    const end = fmtDate(isoDate(sunday));
    return monday.getMonth() === sunday.getMonth() ? `${monday.getDate()}–${end}` : `${fmtDate(isoDate(monday))} – ${end}`;
}

function volumeReadout(n) {
    const w = S.data.weeks[n - 1];
    if (!w) return '';
    const head = `${t('weekN', { w: n })} · ${t(`phase.${w.phase}`)} · ${weekRange(n)}`;
    let body = weekStarted(w) ? t('volDone', { d: realKm(w), p: w.planned_km }) : t('volFuture', { p: w.planned_km });
    if (w.extra_km > 0) body += ` · ${t('volExtra', { e: w.extra_km })}`;
    return `<span><b>${esc(head)}</b><small>${esc(body)}</small></span>
        <button type="button" class="btn ghost small" data-goto-week="${n}">${t('seeWeek')}</button>`;
}

function showVolumeWeek(n) {
    const box = $('#volReadout');
    if (!box) return;
    box.innerHTML = volumeReadout(n);
    $$('.vcol').forEach(c => c.classList.toggle('sel', Number(c.dataset.week) === n));
}

function volumeChart(weeks) {
    const top = Math.max(10, ...weeks.map(w => Math.max(w.planned_km, realKm(w))));
    const step = niceStep(top);
    const yMax = Math.ceil(top / step) * step;
    const pct = v => `${(100 * v / yMax).toFixed(2)}%`;
    const ticks = [];
    for (let v = 0; v <= yMax; v += step) ticks.push(v);
    const sparse = weeks.length > 16;
    const selected = S.volWeek || (weeks.find(w => w.is_current) || weeks[0]).week_number;

    const cols = weeks.map(w => {
        const n = w.week_number;
        const real = realKm(w);
        const light = LIGHT_PHASES.includes(w.phase) ? 'light' : '';
        const label = !sparse || n % 2 === 1 || w.is_current ? n : '';
        return `<button type="button" class="vcol ${w.is_current ? 'current' : ''} ${n === selected ? 'sel' : ''}" data-week="${n}"
                aria-label="${esc(`${t('weekN', { w: n })}: ${weekStarted(w) ? t('volDone', { d: real, p: w.planned_km }) : t('volFuture', { p: w.planned_km })}`)}">
            <span class="vplot">
                <span class="vbar planned ${light}" style="height:${pct(w.planned_km)}"></span>
                ${weekStarted(w) && real > 0 ? `<span class="vbar real" style="height:${pct(real)}"></span>` : ''}
            </span>
            <small>${label}</small>
        </button>`;
    }).join('');

    return `
        <div class="vchart">
            <div class="vaxis">${ticks.map(v => `<span style="bottom:${pct(v)}">${v}</span>`).join('')}</div>
            <div class="vbody">
                <div class="vgrid">${ticks.map(v => `<span style="bottom:${pct(v)}"></span>`).join('')}</div>
                <div class="vcols">${cols}</div>
            </div>
        </div>
        <div class="vlegend">
            <span><i class="sw planned"></i>${t('volPlanned')}</span>
            <span><i class="sw real"></i>${t('volReal')}</span>
            <span><i class="sw planned light"></i>${t('volLight')}</span>
        </div>
        <div class="vreadout" id="volReadout">${volumeReadout(selected)}</div>`;
}

function renderPlanTab() {
    const { plan, weeks } = S.data;

    const list = weeks.map(w => {
        const open = S.openWeeks.has(w.week_number) || (S.openWeeks.size === 0 && w.is_current);
        const first = w.workouts[0];
        const range = first ? fmtDate(first.date) : '';
        return `
            <section class="week ${open ? 'open' : ''} ${w.is_current ? 'current' : ''}" id="week-${w.week_number}">
                <button type="button" class="week-head" data-toggle-week="${w.week_number}">
                    <span><b>${t('weekN', { w: w.week_number })}</b> <span class="phase ph-${w.phase}">${esc(t(`phase.${w.phase}`))}</span></span>
                    <span class="muted small">${range ? esc(range) + ' · ' : ''}${realKm(w)}/${w.planned_km} km</span>
                </button>
                <div class="rows">${w.workouts.map(workoutRow).join('')}</div>
            </section>`;
    }).join('');

    const days = plan.weekly_days.map(d => t('daysShort')[d]).join(' · ');
    const adjusted = plan.volume_factor < 1 ? `<p>${t('volumeAdjusted', { pct: Math.round(plan.volume_factor * 100) })}</p>` : '';
    return `
        <section class="card">
            <div class="card-head"><h2>${t('weekVolume')}</h2></div>
            ${volumeChart(weeks)}
        </section>
        <div class="weeks">${list}</div>
        ${racesCard(S.data.races || [])}
        <section class="plan-meta muted small">
            <p>${esc(plan.target_distance.toUpperCase())} · ${esc(fmtDate(plan.target_date, { day: 'numeric', month: 'long', year: 'numeric' }))} · ${esc(t(`terrainOpt.${plan.terrain}`) || plan.terrain)} · ${esc(days)}</p>
            ${adjusted}
        </section>
        <section class="card plan-history">
            <div class="card-head"><h2>${t('history')}</h2></div>
            <div class="set-row">
                <p class="hint">${t('historyHint')}</p>
                <button type="button" class="btn ghost small" data-action="history">${t('historyOpen')}</button>
            </div>
        </section>
        <div class="actions spread">
            ${plan.finished
                ? `<button type="button" class="btn ghost" data-action="cancel-plan">${t('finishPlan')}</button>`
                : `<button type="button" class="btn ghost danger-text" data-action="cancel-plan">${t('cancelPlan')}</button>`}
            <button type="button" class="btn ghost" data-action="new-plan">${t('newPlan')}</button>
        </div>`;
}

/* -------------------------------------------------------- workout detail */

function paceVerdict(type, c) {
    if (!c) return '';
    const pct = Math.round(Math.abs(c.deviation) * 100);
    const diff = pct ? ` · ${t(`paceDiff.${c.direction}`, { pct })}` : '';
    let tip = '';
    if ((type === 'easy' || type === 'long_run') && c.level !== 'ok' && c.direction === 'fast') tip = t('paceTip.easy_fast');
    else if (type === 'tempo' || type === 'intervals') tip = t(c.basis === 'work' ? 'paceTip.work' : 'paceTip.mean');
    return `<div class="pace-verdict p-${esc(c.level)}">
        <b>${paceIcon(c.level, c.direction)} ${esc(t(`paceLevel.${paceLevelKey(c.level, c.direction)}`))}</b>
        <span>${esc(t('paceCompare', { e: fmtDuration(c.expected_sec_km), a: fmtDuration(c.actual_sec_km) }))}${esc(diff)}</span>
        ${tip ? `<small>${esc(tip)}</small>` : ''}
    </div>`;
}

function workBlocks(work) {
    if (!work || !work.blocks.length) return '';
    const rows = work.blocks.map((b, i) => {
        // Flat-equivalent pace only helps if the grade really shifted it
        const gap = b.gap_sec_km && Math.abs(b.gap_sec_km - b.pace_sec_km) >= 3 ? t('gapShort', { p: fmtDuration(b.gap_sec_km) }) : '';
        const extra = [b.avg_hr ? `♥ ${b.avg_hr}` : '', gap].filter(Boolean).join(' · ');
        return `
        <li class="step k-interval">
            <span>${i + 1} · ${b.km} km</span>
            <span class="step-right"><b>${fmtDuration(b.pace_sec_km)} /km</b>${extra ? `<small>${esc(extra)}</small>` : ''}</span>
        </li>`;
    }).join('');
    let fade = '';
    if (work.fade != null) {
        const pct = Math.round(work.fade * 100);
        fade = `<p class="hint">${esc(pct >= 3 ? t('workFade', { pct }) : t('workEven'))}</p>`;
    }
    return `<h3>${t('workBlocks')}</h3><ol class="steps">${rows}</ol>${fade}`;
}

async function openWorkout(id) {
    let w;
    try {
        w = await api(`/api/workouts/${id}`);
    } catch (e) {
        toast(errText(e), 'error');
        return;
    }
    const steps = (w.steps || []).map(s => `
        <li class="step k-${s.kind}">
            <span>${esc(s.label)}</span>
            <span class="step-right"><b>${esc(s.duration)}</b>${s.pace ? `<small>${esc(s.pace)}</small>` : ''}</span>
        </li>`).join('');
    const actual = w.actual ? `
        <h3>${t('actual')}</h3>
        <div class="stats compact">
            <div class="stat"><span>km</span><b>${w.actual.distance_km}</b></div>
            <div class="stat"><span>${t('pace')}</span><b>${fmtDuration(w.actual.pace_sec_km)}</b></div>
            <div class="stat"><span>⏱</span><b>${fmtDuration(w.actual.duration_sec)}</b></div>
            ${w.actual.avg_hr ? `<div class="stat"><span>♥</span><b>${w.actual.avg_hr}</b></div>` : ''}
        </div>
        ${paceVerdict(w.type, w.actual.pace_check)}
        ${workBlocks(w.actual.work)}` : '';
    const done = w.status === 'completed';
    const actions = done
        ? `<button type="button" class="btn ghost" id="wStatus">${t('unmarkDone')}</button>`
        : `<button type="button" class="btn ghost" id="wMove">${t('move')}</button>
           <button type="button" class="btn primary" id="wStatus">${t('markDone')}</button>`;

    openSheet(w.title, `
        <div class="detail-meta">
            ${typeTag(w.type)}
            <span>${esc(relDay(w.date))}</span>
            <span class="status s-${w.status}">${esc(t(`status.${w.status}`))}</span>
            ${w.on_watch ? `<span class="watch-ok">⌚ ${t('onWatch')}</span>` : ''}
        </div>
        <p class="detail-numbers"><b>${w.distance_km ?? '–'} km</b> · ~${w.duration_min ?? '–'} min</p>
        ${w.description ? `<p class="muted">${esc(w.description)}</p>` : ''}
        ${steps ? `<h3>${t('steps')}</h3><ol class="steps">${steps}</ol>` : ''}
        ${actual}
        ${done ? `<h3>${t('rpeLabel')}</h3>${rpeChips(w.id, w.rpe)}` : ''}
        <p class="about">${esc(t(`about.${w.type}`))}</p>
        <form id="moveForm" class="move-form" hidden>
            <label>${t('moveTo')}<input type="date" id="moveDate" value="${w.date}" min="${todayIso()}" max="${S.data.plan.target_date}" required></label>
            <button type="submit" class="btn primary">${t('save')}</button>
        </form>
        <div class="actions">${actions}</div>`, body => {
        const move = $('#wMove', body);
        if (move) move.onclick = () => { $('#moveForm', body).hidden = false; move.hidden = true; };
        $('#moveForm', body).onsubmit = async e => {
            e.preventDefault();
            try {
                await api(`/api/workouts/${id}/move`, { method: 'POST', body: { new_date: $('#moveDate', body).value } });
                closeSheet();
                toast(t('moved'));
                await reloadPlan();
            } catch (err) { toast(errText(err), 'error'); }
        };
        $('#wStatus', body).onclick = async () => {
            try {
                await api(`/api/workouts/${id}/status`, { method: 'POST', body: { status: done ? 'scheduled' : 'completed' } });
                closeSheet();
                await reloadPlan();
            } catch (err) { toast(errText(err), 'error'); }
        };
    });
}

/* ---------------------------------------------------------------- wizard */

function suggestReference() {
    const pbs = S.pbs || {};
    const available = DISTANCES.filter(d => pbs[d]);
    if (available.length) {
        // The record whose distance is closest to the goal usually predicts best
        const target = DISTANCE_KM[W.distance];
        const best = available.reduce((a, b) => (Math.abs(DISTANCE_KM[a] - target) <= Math.abs(DISTANCE_KM[b] - target) ? a : b));
        return { dist: best, time: fmtDuration(pbs[best]), fromGarmin: true };
    }
    const p = S.profile;
    return p ? { dist: p.reference_distance, time: p.reference_time, fromGarmin: false } : { dist: '10k', time: '55:00', fromGarmin: false };
}

let W = null;

function openWizard() {
    const start = nextMonday();
    W = {
        step: 1,
        name: '',
        distance: '10k',
        start: isoDate(start),
        race: isoDate(addDays(start, 7 * 10 + 5)),
        terrain: 'flat',
        days: new Set([1, 3, 6]),
        longDay: 6,
        level: 'intermediate',
        injury: 'rarely_never',
        ref: null,
        refEdited: false,
        preview: null,
    };
    W.ref = suggestReference();
    renderWizard();
    if (!S.pbs) loadRecords();
}

// Garmin records to suggest the time: fetched when the wizard opens, without blocking it.
// If they arrive later, they replace the suggestion as long as the time hasn't been edited.
async function loadRecords() {
    try {
        S.pbs = (await api('/api/garmin/records')).pbs;
    } catch (e) {
        return;
    }
    if (!W || W.refEdited || $('#sheet').hidden || !Object.keys(S.pbs).length) return;
    W.ref = suggestReference();
    if (W.step === 3) renderWizard();
}

function chips(name, options, selected, labelFn, multi = false) {
    return `<div class="chips" role="group">${options.map(o => {
        const on = multi ? selected.has(o) : selected === o;
        return `<button type="button" class="chip ${on ? 'on' : ''}" data-${name}="${o}" aria-pressed="${on}">${esc(labelFn(o))}</button>`;
    }).join('')}</div>`;
}

function wizardStepHtml() {
    if (W.step === 1) {
        return `
            <label class="field"><span>${t('eventName')}</span><input type="text" id="wName" value="${esc(W.name)}" maxlength="80" placeholder="${esc(t('eventNameHint'))}" autocomplete="off"></label>
            <div class="field"><span>${t('distance')}</span>${chips('distance', DISTANCES, W.distance, d => d.toUpperCase())}</div>
            <div class="field-row">
                <label class="field"><span>${t('raceDate')}</span><input type="date" id="wRace" value="${W.race}" min="${W.start}"></label>
                <label class="field"><span>${t('startDate')}</span><input type="date" id="wStart" value="${W.start}" min="${todayIso()}"></label>
            </div>
            <p class="hint" id="wWeeks"></p>
            <div class="field"><span>${t('terrain')}</span>${chips('terrain', ['flat', 'rolling', 'hilly'], W.terrain, o => t(`terrainOpt.${o}`))}</div>`;
    }
    if (W.step === 2) {
        const dayIdx = [0, 1, 2, 3, 4, 5, 6];
        const selected = dayIdx.filter(d => W.days.has(d));
        return `
            <div class="field"><span>${t('runDays')}</span>${chips('day', dayIdx, W.days, d => t('daysShort')[d], true)}</div>
            <div class="field"><span>${t('longRunDay')}</span>${chips('long', selected, W.longDay, d => t('daysShort')[d])}</div>
            <div class="field"><span>${t('level')}</span>${chips('level', Object.keys(I18N.es.levelOpt), W.level, o => t(`levelOpt.${o}`))}</div>
            <div class="field"><span>${t('injury')}</span>${chips('injury', Object.keys(I18N.es.injuryOpt), W.injury, o => t(`injuryOpt.${o}`))}</div>`;
    }
    return `
        <div class="field"><span>${t('refMark')}</span>${chips('refdist', DISTANCES, W.ref.dist, d => d.toUpperCase())}</div>
        <label class="field"><span>${t('refTime')}</span><input type="text" id="wTime" inputmode="numeric" value="${esc(W.ref.time)}" placeholder="50:00" autocomplete="off"></label>
        <p class="hint">${W.ref.fromGarmin ? `${t('fromGarmin')}. ` : ''}${t('refHint')}</p>
        <div class="summary" id="wSummary"></div>`;
}

function renderWizard() {
    const last = W.step === 3;
    openSheet(t('wizTitle'), `
        <div class="wiz-progress"><span style="width:${W.step * 33.34}%"></span></div>
        <p class="eyebrow">${t('wizStep', { s: W.step })} · ${t(['wizRace', 'wizWeek', 'wizMark'][W.step - 1])}</p>
        <div class="wiz-body">${wizardStepHtml()}</div>
        <div class="actions spread">
            <button type="button" class="btn ghost" id="wBack" ${W.step === 1 ? 'data-close' : ''}>${W.step === 1 ? t('cancel') : t('back')}</button>
            <button type="button" class="btn primary" id="wNext">${last ? t('createPlan') : t('next')}</button>
        </div>`, bindWizard);
}

function bindWizard(body) {
    body.onclick = e => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        const ds = chip.dataset;
        if (ds.distance) { W.distance = ds.distance; W.ref = W.ref.fromGarmin ? suggestReference() : W.ref; }
        if (ds.terrain) W.terrain = ds.terrain;
        if (ds.day !== undefined) {
            const d = Number(ds.day);
            if (W.days.has(d)) { if (W.days.size > 2) W.days.delete(d); } else W.days.add(d);
            if (!W.days.has(W.longDay)) W.longDay = Math.max(...W.days);
        }
        if (ds.long !== undefined) W.longDay = Number(ds.long);
        if (ds.level) W.level = ds.level;
        if (ds.injury) W.injury = ds.injury;
        if (ds.refdist) { W.ref = { ...W.ref, dist: ds.refdist, fromGarmin: false }; W.refEdited = true; captureTime(body); }
        captureInputs(body);
        renderWizard();
    };

    const race = $('#wRace', body), start = $('#wStart', body), time = $('#wTime', body);
    if (race) race.onchange = () => { captureInputs(body); updatePreview(); };
    if (start) start.onchange = () => { captureInputs(body); race.min = W.start; updatePreview(); };
    if (time) time.oninput = () => { maskDurationInput(time); W.refEdited = true; captureTime(body); updatePreview(); };

    $('#wBack', body).onclick = e => {
        if (W.step === 1) return closeSheet();
        e.stopPropagation();
        captureInputs(body);
        W.step -= 1;
        renderWizard();
    };
    $('#wNext', body).onclick = async e => {
        e.stopPropagation();
        captureInputs(body);
        if (W.step < 3) { W.step += 1; renderWizard(); return; }
        await submitWizard(e.target);
    };
    updatePreview();
}

function captureInputs(body) {
    const race = $('#wRace', body), start = $('#wStart', body), name = $('#wName', body);
    if (name) W.name = name.value;
    if (race && race.value) W.race = race.value;
    if (start && start.value) W.start = start.value;
    captureTime(body);
}

function captureTime(body) {
    const time = $('#wTime', body);
    if (time) W.ref = { ...W.ref, time: time.value, fromGarmin: W.ref.fromGarmin && time.value === W.ref.time };
}

let previewTimer = null;
function updatePreview() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(async () => {
        const sec = parseDuration(W.ref.time);
        const params = {
            target_distance: W.distance, target_date: W.race, start_date: W.start,
            running_level: W.level, injury_history: W.injury, terrain: W.terrain,
        };
        if (sec) Object.assign(params, { reference_distance: W.ref.dist, reference_time_sec: sec });
        try {
            W.preview = await api('/api/plans/preview', { method: 'POST', body: params });
        } catch (e) {
            W.preview = null;
        }
        paintPreview();
    }, 200);
}

function paintPreview() {
    const p = W.preview;
    const weeksEl = $('#wWeeks');
    if (weeksEl) {
        if (!p || p.weeks < 1) weeksEl.textContent = '';
        else {
            const r = p.recommendation;
            const short = p.weeks < r.min;
            weeksEl.className = `hint ${short ? 'warn' : ''}`;
            weeksEl.textContent = `${t('weeksInfo', { w: p.weeks })} · ${t('weeksRec', r)}${short ? '. ' + t('weeksShort') : ''}`;
        }
    }
    const sum = $('#wSummary');
    if (sum) {
        const valid = p && parseDuration(W.ref.time) > 0;
        sum.innerHTML = valid ? `
            <div class="stat"><span>${t('estimated')} ${W.distance.toUpperCase()}</span><b>${esc(p.prediction.formatted_nominal)}</b></div>
            <div class="stat"><span>${t('pace')}</span><b>${esc(p.prediction.formatted_pace)}</b></div>
            <div class="stat"><span>${t('vdot')}</span><b>${fmtVdot(p.vdot)}</b></div>
            <div class="stat"><span>${t('weeksInfo', { w: '' }).trim()}</span><b>${p.weeks}</b></div>` : `<p class="hint warn">${t('err.invalid_time')}</p>`;
    }
}

async function submitWizard(btn) {
    const sec = parseDuration(W.ref.time);
    if (!sec) { toast(t('err.invalid_time'), 'error'); return; }
    btn.disabled = true;
    btn.textContent = t('creating');
    try {
        await api('/api/plans', {
            method: 'POST',
            body: {
                name: W.name.trim() || null,
                target_distance: W.distance, target_date: W.race, start_date: W.start,
                weekly_days: [...W.days].sort(), long_run_day: W.longDay,
                terrain: W.terrain, running_level: W.level, injury_history: W.injury,
                reference_distance: W.ref.dist, reference_time_sec: sec,
            },
        });
        closeSheet();
        toast(t('planCreated'));
        S.tab = 'today';
        S.openWeeks.clear();
        await loadAll();
    } catch (e) {
        toast(errText(e), 'error');
        btn.disabled = false;
        btn.textContent = t('createPlan');
    }
}

function startNewPlan() {
    if (S.data && S.data.active) {
        const msg = S.data.plan.finished ? 'newPlanFinishedMsg' : 'newPlanMsg';
        confirmSheet(t('newPlan'), t(msg), t('newPlan'), async () => openWizard());
    } else {
        openWizard();
    }
}

/* -------------------------------------------------------------- settings */

// Palettes: swatch for the picker and per-mode background for the browser bar
const PALETTES = {
    classic: { swatch: 'linear-gradient(135deg, #22c3dd, #0891b2)', bg: { dark: '#0b0f19', light: '#eef1f6' } },
    track: { swatch: 'linear-gradient(135deg, #e0492a, #f08a4b)', bg: { dark: '#14100e', light: '#f5eee5' } },
    volt: { swatch: 'linear-gradient(135deg, #c6f432 50%, #0b1320 50%)', bg: { dark: '#090c10', light: '#eaeff3' } },
    dawn: { swatch: 'linear-gradient(135deg, #ff7a59, #ff3d77)', bg: { dark: '#13112a', light: '#fcf1ec' } },
};

function currentPalette() {
    const v = document.documentElement.getAttribute('data-palette');
    return Object.hasOwn(PALETTES, v) ? v : 'classic';
}

function setPalette(value) {
    if (Object.hasOwn(PALETTES, value) && value !== 'classic') document.documentElement.setAttribute('data-palette', value);
    else document.documentElement.removeAttribute('data-palette');
    writeStorage('gc_palette', value);
    syncThemeColor();
}

// Browser status bar color matching the theme and palette
function syncThemeColor() {
    const theme = currentTheme();
    const bg = PALETTES[currentPalette()].bg;
    $$('meta[name="theme-color"]').forEach(m => {
        const dark = theme === 'system' ? (m.getAttribute('media') || '').includes('dark') : theme === 'dark';
        m.setAttribute('content', dark ? bg.dark : bg.light);
    });
}

function currentTheme() {
    const v = document.documentElement.getAttribute('data-theme');
    return v === 'light' || v === 'dark' ? v : 'system';
}

function setTheme(value) {
    if (value === 'light' || value === 'dark') document.documentElement.setAttribute('data-theme', value);
    else document.documentElement.removeAttribute('data-theme');
    writeStorage('gc_theme', value);
    syncThemeColor();
}

function openSettings() {
    const p = S.profile || { paces: {}, vdot: '–', reference_distance: '10k', reference_time: '' };
    const paces = Object.entries(p.paces).map(([k, v]) =>
        `<li><span>${esc(t(`paceNames.${k}`))}</span><b>${esc(v)} /km</b></li>`).join('');

    openSheet(t('settings'), `
        <section class="set">
            <h3>${t('garminAccount')}</h3>
            <div class="set-row">
                <p>${esc(t('connectedAs', { n: S.me.name || 'Garmin' }))}${S.garmin.connected ? '' : ` · <span class="danger-text">${t('notConnected')}</span>`}</p>
                <div class="set-actions">
                    ${S.garmin.connected ? '' : `<button type="button" class="btn primary small" data-action="connect">${t('reconnect')}</button>`}
                    <button type="button" class="btn ghost small" id="sLogout">${t('signOut')}</button>
                </div>
            </div>
            ${S.garmin.pending_deletions ? `<p class="hint warn">${t('pendingDeletions', { n: S.garmin.pending_deletions })}</p>` : ''}
            ${S.garmin.connected && S.data && S.data.active ? `<div class="set-row">
                <p class="hint">${t('syncHint')}</p>
                <button type="button" class="btn ghost small" data-action="sync">${t('syncNow')}</button>
            </div>` : ''}
        </section>
        <section class="set">
            <h3>${t('language')}</h3>
            ${chips('lang', ['es', 'en'], S.lang, l => (l === 'es' ? 'Español' : 'English'))}
            <p class="hint">${t('languageHint')}</p>
        </section>
        <section class="set">
            <h3>${t('theme')}</h3>
            ${chips('apptheme', ['system', 'light', 'dark'], currentTheme(), o => t(`themeOpt.${o}`))}
            <h3>${t('palette')}</h3>
            <div class="chips" role="group">${Object.keys(PALETTES).map(k => {
                const on = currentPalette() === k;
                return `<button type="button" class="chip ${on ? 'on' : ''}" data-apppalette="${k}" aria-pressed="${on}"><i class="swatch" style="background:${PALETTES[k].swatch}"></i>${esc(t(`paletteOpt.${k}`))}</button>`;
            }).join('')}</div>
            <p class="hint">${t('themeHint')}</p>
        </section>
        <section class="set">
            <h3>${t('paces')} <span class="muted small">${t('vdot')} ${S.profile ? fmtVdot(p.vdot) : p.vdot}</span></h3>
            <ul class="paces">${paces}</ul>
            <form id="sMark" class="field-row">
                <label class="field"><span>${t('distance')}</span>
                    <select id="sDist">${DISTANCES.map(d => `<option value="${d}" ${d === p.reference_distance ? 'selected' : ''}>${d.toUpperCase()}</option>`).join('')}</select>
                </label>
                <label class="field"><span>${t('refTime')}</span><input type="text" id="sTime" inputmode="numeric" value="${esc(p.reference_time)}"></label>
                <button type="submit" class="btn ghost small">${t('updateMark')}</button>
            </form>
        </section>
        <details class="set">
            <summary>${t('advanced')}</summary>
            <p class="hint">${t('cleanHint')}</p>
            <button type="button" class="btn ghost small" id="sClean" ${S.garmin.connected ? '' : 'disabled'}>${t('cleanCalendar')}</button>
            ${S.me.admin ? `<h3>${t('database')}</h3>
            <p class="hint">${t('backupHint')}</p>
            <div class="set-actions">
                <a class="btn ghost small" href="/api/backup/download" download>${t('backupDownload')}</a>
                <button type="button" class="btn ghost small" id="sRestore">${t('backupRestore')}</button>
                <input type="file" id="sRestoreFile" accept=".db,.sqlite,.sqlite3,application/x-sqlite3" hidden>
            </div>` : ''}
            <p class="hint">${t('deleteAccountMsg')}</p>
            <button type="button" class="btn ghost small danger-text" id="sDelete">${t('deleteAccount')}</button>
        </details>`, body => {
        body.onclick = async e => {
            const lang = e.target.closest('[data-lang]');
            const theme = e.target.closest('[data-apptheme]');
            const palette = e.target.closest('[data-apppalette]');
            if (theme || palette) {
                if (theme) setTheme(theme.dataset.apptheme);
                else setPalette(palette.dataset.apppalette);
                const chosen = theme || palette;
                const attr = theme ? '[data-apptheme]' : '[data-apppalette]';
                $$(attr, body).forEach(c => {
                    const on = c === chosen;
                    c.classList.toggle('on', on);
                    c.setAttribute('aria-pressed', String(on));
                });
                return;
            }
            if (!lang || lang.dataset.lang === S.lang) return;
            try {
                S.profile = await api('/api/profile', { method: 'PUT', body: { language: lang.dataset.lang } });
                S.me.language = S.profile.language;
                setLang(S.profile.language, false);
                await reloadPlan();
                openSettings();
            } catch (err) { toast(errText(err), 'error'); }
        };
        const sTime = $('#sTime', body);
        sTime.oninput = () => maskDurationInput(sTime);
        $('#sLogout', body).onclick = async () => {
            await api('/api/auth/logout', { method: 'POST' }).catch(() => {});
            signedOut();
        };
        $('#sMark', body).onsubmit = async e => {
            e.preventDefault();
            const sec = parseDuration($('#sTime', body).value);
            if (!sec) { toast(t('err.invalid_time'), 'error'); return; }
            try {
                S.profile = await api('/api/profile', { method: 'PUT', body: { reference_distance: $('#sDist', body).value, reference_time_sec: sec } });
                toast(t('marksUpdated'));
                await reloadPlan();
                openSettings();
            } catch (err) { toast(errText(err), 'error'); }
        };
        if (S.me.admin) {  // the database section only exists for the admin
            $('#sRestore', body).onclick = () => $('#sRestoreFile', body).click();
            $('#sRestoreFile', body).onchange = e => {
                const file = e.target.files[0];
                if (!file) return;
                confirmSheet(t('restoreTitle'), t('restoreMsg', { f: file.name }), t('backupRestore').replace('…', ''), async () => {
                    toast(t('restoring'));
                    try {
                        // The file goes as-is in the body (not JSON): bypasses api()
                        const res = await fetch('/api/backup/restore', {
                            method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: file,
                        }).catch(() => { throw new Error('network'); });
                        const data = await res.json().catch(() => ({}));
                        if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'generic');
                        toast(t('restored'));
                        // Profiles, plans and the session itself may have changed: reload everything
                        setTimeout(() => location.reload(), 900);
                    } catch (err) { toast(errText(err), 'error'); closeSheet(); }
                });
            };
        }
        $('#sClean', body).onclick = () => confirmSheet(t('cleanCalendar'), t('cleanHint'), t('confirm'), async () => {
            try {
                const res = await api('/api/garmin/clean-calendar', { method: 'POST' });
                closeSheet();
                toast(t('cleanDone', { n: res.removed }));
                await reloadPlan();
            } catch (err) { toast(errText(err), 'error'); closeSheet(); }
        });
        $('#sDelete', body).onclick = () => confirmSheet(t('deleteAccount'), t('deleteAccountMsg'), t('deleteAccount'), async () => {
            try {
                await api('/api/me', { method: 'DELETE' });
                toast(t('accountDeleted'));
                signedOut();
            } catch (err) { toast(errText(err), 'error'); closeSheet(); }
        });
    });
}

function historyCard(p) {
    const a = p.adherence;
    const full = { day: 'numeric', month: 'short', year: 'numeric' };
    const meta = [`${fmtDate(p.start_date)} – ${fmtDate(p.target_date, full)}`, t('histWeeks', { n: p.total_weeks })];
    if (p.reviews_accepted) meta.push(t('histReviews', { n: p.reviews_accepted }));
    const race = p.race ? `<p class="hist-race"><b>${t('histRace')} ${fmtDuration(p.race.time_sec)}</b>
        · ${fmtDuration(p.race.pace_sec_km)} /km · <span class="muted">${esc(t('histPredicted', { p: fmtDuration(p.predicted_sec) }))}</span></p>` : '';
    const vdot = p.vdot_start === p.vdot_end ? fmtVdot(p.vdot_end) : `${fmtVdot(p.vdot_start)} → ${fmtVdot(p.vdot_end)}`;
    return `<article class="hist">
        <div class="hist-head">
            <b>${esc(p.name)}</b>
            <span class="status ps-${esc(p.status)}">${esc(t(`planStatus.${p.status}`))}</span>
        </div>
        <p class="muted small">${esc(meta.join(' · '))}</p>
        ${race}
        <div class="stats compact">
            <div class="stat"><span>${t('histSessions')}</span><b>${a.sessions.done}/${a.sessions.total}</b>${a.sessions.pct != null ? `<small>${a.sessions.pct}%</small>` : ''}</div>
            <div class="stat"><span>km</span><b>${a.km.done}</b><small>/ ${a.km.planned}</small></div>
            <div class="stat"><span>${t('vdot')}</span><b>${vdot}</b></div>
            ${a.pace.checked ? `<div class="stat"><span>${t('histPace')}</span><b>${a.pace.pct}%</b></div>` : ''}
        </div>
    </article>`;
}

async function openHistory() {
    let res;
    try {
        res = await api('/api/plans/history');
    } catch (e) {
        toast(errText(e), 'error');
        return;
    }
    openSheet(t('history'), res.plans.length ? res.plans.map(historyCard).join('') : `<p class="muted">${t('historyEmpty')}</p>`);
}

function openHelp() {
    openSheet(t('helpOpen'), helpHtml(S.lang));
}

function signedOut() {
    closeSheet();
    Object.assign(S, { me: null, data: null, profile: null, garmin: { connected: false }, pbs: null, progress: null, tab: 'today' });
    S.openWeeks.clear();
    render();
}

/* --------------------------------------------------------------- connect */

function connectFormHtml() {
    return `
        <form class="stack" data-form="token">
            <p class="hint">${t('tokenHint')}</p>
            <label class="field"><span>${t('tokenFile')}</span><input type="file" name="file" accept=".json,application/json"></label>
            <label class="field"><span>${t('tokenPaste')}</span><textarea name="json" rows="3" spellcheck="false"></textarea></label>
            <button type="submit" class="btn primary">${t('connect')}</button>
        </form>
        <details class="set">
            <summary>${t('useLogin')}</summary>
            <form class="stack" data-form="login">
                <label class="field"><span>${t('email')}</span><input type="email" name="email" autocomplete="username" required></label>
                <label class="field"><span>${t('password')}</span><input type="password" name="password" autocomplete="current-password" required></label>
                <p class="hint">${t('loginHint')}</p>
                <button type="submit" class="btn ghost">${t('signIn')}</button>
            </form>
            <form class="stack" data-form="mfa" hidden>
                <p class="hint">${t('mfaHint')}</p>
                <label class="field"><span>${t('mfaTitle')}</span><input type="text" name="code" inputmode="numeric" autocomplete="one-time-code" required class="code"></label>
                <button type="submit" class="btn ghost">${t('verify')}</button>
            </form>
        </details>`;
}

/** Wires up the Garmin sign-in form (login screen or reconnect sheet). */
function bindConnect(root) {
    const form = name => $(`[data-form="${name}"]`, root);
    let mfaSession = null;
    const busy = (f, on) => { $('button[type=submit]', f).disabled = on; };
    const submit = async (f, path, body, onResult) => {
        busy(f, true);
        try {
            const res = await api(path, { method: 'POST', body });
            if (onResult && onResult(res)) return;
            closeSheet();
            toast(t('connected'));
            await loadAll();
        } catch (err) {
            toast(errText(err), 'error');
            if (err.message === 'mfa_expired') { form('mfa').hidden = true; form('login').hidden = false; }
        } finally {
            busy(f, false);
        }
    };
    form('login').onsubmit = e => {
        e.preventDefault();
        const f = e.target;
        submit(f, '/api/auth/login', { email: f.email.value, password: f.password.value, language: S.lang }, res => {
            if (res.status !== 'mfa_required') return false;
            mfaSession = res.session_id;
            form('login').hidden = true;
            form('mfa').hidden = false;
            form('mfa').code.focus();
            return true;
        });
    };
    form('mfa').onsubmit = e => {
        e.preventDefault();
        submit(e.target, '/api/auth/mfa', { session_id: mfaSession, mfa_code: e.target.code.value, language: S.lang });
    };
    form('token').file.onchange = async e => {
        const file = e.target.files[0];
        if (file) form('token').json.value = await file.text();
    };
    form('token').onsubmit = e => {
        e.preventDefault();
        const json = e.target.json.value.trim();
        if (json) submit(e.target, '/api/auth/token', { token_json: json, language: S.lang });
    };
}

function openConnect() {
    openSheet(t('reconnect'), connectFormHtml(), bindConnect);
}

/* ---------------------------------------------------------------- events */

async function onAction(action, el) {
    if (action === 'connect') return openConnect();
    if (action === 'new-plan') return startNewPlan();
    if (action === 'history') return openHistory();
    if (action === 'reload') { el.disabled = true; return loadAll(); }
    if (action === 'reload-progress') { S.progressError = false; return render(); }
    if (action === 'cancel-plan') {
        const key = S.data.plan.finished ? 'finishPlan' : 'cancelPlan';
        return confirmSheet(t(key), t(`${key}Msg`), t(key), async () => {
            try {
                const res = await api(`/api/plans/${S.data.plan.id}/cancel`, { method: 'POST' });
                closeSheet();
                toast(t(res.status === 'completed' ? 'planFinished' : 'planCancelled'));
                S.tab = 'today';
                await reloadPlan();
            } catch (err) { toast(errText(err), 'error'); closeSheet(); }
        });
    }
    if (action === 'review-submit' || action === 'review-skip') {
        el.disabled = true;
        const body = action === 'review-skip' ? { skip: true } : { ...S.reviewAnswers };
        try {
            await api('/api/plans/active/review', { method: 'POST', body });
            S.reviewAnswers = { fatigue: null, pain: null };
            await reloadPlan();
        } catch (err) { toast(errText(err), 'error'); el.disabled = false; }
        return;
    }
    if (action === 'review-accept' || action === 'review-decline') {
        el.disabled = true;
        const accept = action === 'review-accept';
        try {
            await api(`/api/plans/active/review/${el.dataset.review}`, { method: 'POST', body: { accept } });
            const changed = accept && S.data.review.proposal.changes;
            if (S.data.review.proposal.changes) toast(t(changed ? 'reviewApplied' : 'reviewKept'));
            S.profile = await api('/api/profile');
            await reloadPlan();
        } catch (err) { toast(errText(err), 'error'); el.disabled = false; }
        return;
    }
    if (action === 'race-add') return openAddRace();
    if (action === 'race-delete') {
        return confirmSheet(t('raceDelete'), t('raceDeleteMsg'), t('raceDelete'), async () => {
            try {
                await api(`/api/plans/active/races/${el.dataset.race}`, { method: 'DELETE' });
                closeSheet();
                toast(t('raceDeleted'));
                await reloadPlan();
            } catch (err) { toast(errText(err), 'error'); closeSheet(); }
        });
    }
    if (action === 'race-vdot-accept' || action === 'race-vdot-dismiss') {
        el.disabled = true;
        const accept = action === 'race-vdot-accept';
        try {
            await api(`/api/plans/active/races/${el.dataset.race}/vdot`, { method: 'POST', body: { accept } });
            toast(t(accept ? 'raceVdotApplied' : 'raceVdotKept'));
            if (accept) S.profile = await api('/api/profile');
            await reloadPlan();
        } catch (err) { toast(errText(err), 'error'); el.disabled = false; }
        return;
    }
    if (action === 'sync') {
        el.disabled = true;
        try {
            const res = await api('/api/plans/active/sync', { method: 'POST' });
            const msg = res.imported ? t('syncResult', { a: res.imported, n: res.synced }) : t('synced', { n: res.synced });
            toast(msg, res.errors || res.imported === null ? 'error' : 'ok');
            closeSheet();
            await reloadPlan();
        } catch (err) { toast(errText(err), 'error'); el.disabled = false; }
    }
}

document.addEventListener('click', e => {
    if (e.target.closest('[data-close]')) { closeSheet(); return; }
    const action = e.target.closest('[data-action]');
    if (action) { onAction(action.dataset.action, action); return; }
    const answer = e.target.closest('[data-rfatigue], [data-rpain]');
    if (answer) {
        if (answer.dataset.rfatigue) S.reviewAnswers.fatigue = answer.dataset.rfatigue;
        if (answer.dataset.rpain) S.reviewAnswers.pain = answer.dataset.rpain;
        render();
        return;
    }
    const rpe = e.target.closest('[data-rpe]');
    if (rpe) { saveRpe(Number(rpe.dataset.rpeWorkout), Number(rpe.dataset.rpe), rpe); return; }
    const workout = e.target.closest('[data-workout]');
    if (workout) { openWorkout(Number(workout.dataset.workout)); return; }
    const weekToggle = e.target.closest('[data-toggle-week]');
    if (weekToggle) {
        const n = Number(weekToggle.dataset.toggleWeek);
        const el = $(`#week-${n}`);
        if (S.openWeeks.size === 0) {
            const current = S.data.weeks.find(w => w.is_current);
            if (current) S.openWeeks.add(current.week_number);
        }
        if (S.openWeeks.has(n)) S.openWeeks.delete(n); else S.openWeeks.add(n);
        el.classList.toggle('open', S.openWeeks.has(n));
        return;
    }
    const bar = e.target.closest('[data-week]');
    if (bar) {
        S.volWeek = Number(bar.dataset.week);
        showVolumeWeek(S.volWeek);
        return;
    }
    const goto = e.target.closest('[data-goto-week]');
    if (goto) {
        const n = Number(goto.dataset.gotoWeek);
        S.openWeeks.add(n);
        const el = $(`#week-${n}`);
        el.classList.add('open');
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});

async function saveRpe(workoutId, value, chip) {
    try {
        await api(`/api/workouts/${workoutId}/rpe`, { method: 'POST', body: { rpe: value } });
        $$('.chip', chip.parentElement).forEach(c => c.classList.toggle('on', c === chip));
        toast(t('rpeSaved'));
        const inSheet = !$('#sheet').hidden;
        S.data = await api('/api/plans/active');
        S.progress = null;  // effort changes the load
        if (!inSheet) render();
    } catch (err) { toast(errText(err), 'error'); }
}

// Volume chart readout: on hover or focus of a week; on leave it returns to the selected one
function volumeHover(e) {
    const col = e.target.closest && e.target.closest('.vcol');
    if (col) showVolumeWeek(Number(col.dataset.week));
}
document.addEventListener('pointerover', e => { if (e.pointerType === 'mouse') volumeHover(e); });
document.addEventListener('focusin', volumeHover);
document.addEventListener('pointerout', e => {
    if (e.pointerType !== 'mouse' || !e.target.closest || !e.target.closest('.vchart')) return;
    if (e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest('.vchart')) return;
    const current = S.data && S.data.weeks && S.data.weeks.find(w => w.is_current);
    showVolumeWeek(S.volWeek || (current ? current.week_number : 1));
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !$('#sheet').hidden) closeSheet();
});

$('#profileBtn').onclick = openSettings;
$('#helpBtn').onclick = openHelp;
$$('#tabs .tab').forEach(b => {
    b.onclick = () => {
        if (S.tab === b.dataset.tab) { window.scrollTo({ top: 0, behavior: 'smooth' }); return; }
        S.tab = b.dataset.tab;
        render();
        window.scrollTo({ top: 0 });
    };
});

// Top bar: solid with the small title as soon as the large title scrolls out of view
function updateTopbar() {
    $('#topbar').classList.toggle('scrolled', window.scrollY > 36);
}
window.addEventListener('scroll', updateTopbar, { passive: true });
updateTopbar();

// Sheet: drag down from the header to close
(function sheetDrag() {
    const panel = $('.sheet-panel');
    let startY = null;
    let dy = 0;
    $('#sheetHead').addEventListener('pointerdown', e => {
        if (e.target.closest('button') || window.matchMedia('(min-width: 720px)').matches) return;
        startY = e.clientY;
        dy = 0;
        panel.classList.add('dragging');
        panel.classList.remove('settle');
        $('#sheetHead').setPointerCapture(e.pointerId);
    });
    $('#sheetHead').addEventListener('pointermove', e => {
        if (startY == null) return;
        dy = Math.max(0, e.clientY - startY);
        panel.style.transform = `translateY(${dy}px)`;
    });
    const end = () => {
        if (startY == null) return;
        startY = null;
        panel.classList.remove('dragging');
        if (dy > 110) {
            closeSheet();
        } else {
            panel.classList.add('settle');
            panel.style.transform = '';
        }
    };
    $('#sheetHead').addEventListener('pointerup', end);
    $('#sheetHead').addEventListener('pointercancel', end);
})();

document.documentElement.lang = S.lang;
syncThemeColor();
loadAll();
