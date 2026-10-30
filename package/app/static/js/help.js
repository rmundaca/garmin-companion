/* Garmin Companion — content of the "How it works" sheet (ES/EN).
   Formulas are written in MathML, which browsers render natively. */

/* ------------------------------------------------------------- MathML */

const HelpMath = (() => {
    // Number with the language's decimal separator
    const num = (lang, value) => `<mn>${lang === 'es' ? value.replace('.', ',') : value}</mn>`;
    const block = body => `<math display="block">${body}</math>`;
    const inline = body => `<math>${body}</math>`;
    const vo2 = '<msub><mi mathvariant="normal">VO</mi><mn>2</mn></msub>';
    const pctMax = lang => `<msub><mi mathvariant="normal">%</mi><mtext>${lang === 'es' ? 'máx' : 'max'}</mtext></msub>`;
    const exp = (lang, k, x) => `<msup><mi>e</mi><mrow><mo>−</mo>${num(lang, k)}<mo>&#x2062;</mo><mi>${x}</mi></mrow></msup>`;

    return {
        v: inline('<mi>v</mi>'),
        t: inline('<mi>t</mi>'),
        vo2: inline(vo2),
        vo2Formula: lang => block(`<mrow>${vo2}<mo>(</mo><mi>v</mi><mo>)</mo><mo>=</mo><mo>−</mo>${num(lang, '4.60')}<mo>+</mo>`
            + `${num(lang, '0.182258')}<mo>&#x2062;</mo><mi>v</mi><mo>+</mo>${num(lang, '0.000104')}<mo>&#x2062;</mo><msup><mi>v</mi><mn>2</mn></msup></mrow>`),
        pctFormula: lang => block(`<mrow>${pctMax(lang)}<mo>(</mo><mi>t</mi><mo>)</mo><mo>=</mo>${num(lang, '0.8')}<mo>+</mo>`
            + `${num(lang, '0.1894393')}<mo>&#x2062;</mo>${exp(lang, '0.012778', 't')}<mo>+</mo>`
            + `${num(lang, '0.2989558')}<mo>&#x2062;</mo>${exp(lang, '0.1932605', 't')}</mrow>`),
        vdotFormula: lang => block(`<mrow><mi mathvariant="normal">VDOT</mi><mo>=</mo><mfrac>`
            + `<mrow>${vo2}<mo>(</mo><mi>v</mi><mo>)</mo></mrow><mrow>${pctMax(lang)}<mo>(</mo><mi>t</mi><mo>)</mo></mrow></mfrac></mrow>`),
        loadFormula: (load, duration) => block(`<mrow><mtext>${load}</mtext><mo>=</mo><mtext>${duration}</mtext>`
            + '<mo>×</mo><mtext>RPE (1–10)</mtext></mrow>'),
        acwrOptimal: lang => inline(`<mrow>${num(lang, '0.8')}<mo>≤</mo><mi mathvariant="normal">ACWR</mi><mo>≤</mo>${num(lang, '1.3')}</mrow>`),
        acwrAbove: (lang, value) => inline(`<mrow><mi mathvariant="normal">ACWR</mi><mo>&gt;</mo>${num(lang, value)}</mrow>`),
        hrRange: hr => inline(`<mrow><mn>90</mn><mtext>&#x2009;ppm</mtext><mo>≤</mo><mi mathvariant="normal">${hr}</mi>`
            + '<mo>≤</mo><mn>200</mn><mtext>&#x2009;ppm</mtext></mrow>'),
        times: (lang, value) => inline(`<mrow><mo>×</mo>${num(lang, value)}</mrow>`),
        below: value => inline(`<mrow><mo>&lt;</mo><mn>${value}</mn><mo>%</mo></mrow>`),
        percent: value => inline(`<mrow><mn>${value}</mn><mo>%</mo></mrow>`),
        plus: (lang, value) => inline(`<mrow><mo>+</mo>${num(lang, value)}</mrow>`),
        value: (lang, value) => inline(num(lang, value)),
    };
})();

/* -------------------------------------------------------------- content */

function helpTable(head, rows) {
    return `<div class="help-table"><table>
        <thead><tr>${head.map(h => `<th scope="col">${h}</th>`).join('')}</tr></thead>
        <tbody>${rows.map(r => `<tr>${r.map((c, i) => (i === 0 ? `<th scope="row">${c}</th>` : `<td>${c}</td>`)).join('')}</tr>`).join('')}</tbody>
    </table></div>`;
}

const HELP = {
    es: () => {
        const M = HelpMath;
        const l = 'es';
        return `
        <p class="help-lead">Esta documentación detalla la arquitectura de lógica, los modelos fisiológicos y las reglas de adaptación implementadas en la aplicación.</p>

        <h3>1. Arquitectura y resumen del sistema</h3>
        <p>El sistema genera planes de carrera individualizados mediante un enfoque algorítmico estructurado:</p>
        <ul>
            <li><b>Modelo base:</b> entrenamiento por ritmos derivado de las fórmulas de VDOT de Jack Daniels y Jimmy Gilbert.</li>
            <li><b>Periodización:</b> distribución en macro y microciclos con fases de base, construcción, pico, descarga y <i>taper</i>.</li>
            <li><b>Distribución de carga:</b> adopción del principio de polarización de la intensidad (modelo aproximado 80/20).</li>
            <li><b>Bucle adaptativo:</b> evaluación periódica automatizada basada en la telemetría de Garmin Connect y la realimentación subjetiva del usuario (RPE, fatiga, molestias).</li>
        </ul>

        <h3>2. Fundamento fisiológico: el modelo VDOT</h3>
        <p>El motor calcula la capacidad aeróbica efectiva integrando la economía de carrera (consumo de oxígeno en función de la velocidad) y la fatiga acumulada en función del tiempo de esfuerzo, basadas en los estudios de Jack Daniels y Jimmy Gilbert.</p>

        <h4>2.1 Ecuaciones de cálculo</h4>
        <p>Dada una marca de referencia a una velocidad ${M.v} (metros por minuto):</p>
        <ol>
            <li><b>Coste de oxígeno (${M.vo2}):</b>${M.vo2Formula(l)}</li>
            <li><b>Fracción sostenible del máximo</b> para una duración ${M.t} (minutos):${M.pctFormula(l)}</li>
            <li><b>Valor VDOT:</b>${M.vdotFormula(l)}</li>
        </ol>

        <h4>2.2 Zonas de intensidad</h4>
        <p>A partir del VDOT calculado se configuran cinco ritmos operativos, resolviendo la inversa de la curva de consumo de oxígeno para porcentajes específicos de la capacidad total:</p>
        <ul>
            <li><b>E (Easy / Suave):</b> 62 % – 72 % del VDOT. Destinado a recuperación y base aeróbica.</li>
            <li><b>M (Maratón):</b> 82 % del VDOT. Ritmo específico de competición de larga distancia.</li>
            <li><b>T (Threshold / Umbral):</b> 88 % del VDOT. Optimización del umbral de lactato.</li>
            <li><b>I (Intervals / Intervalos):</b> 98 % del VDOT. Estímulo directo del VO₂máx.</li>
            <li><b>R (Repetitions / Repeticiones):</b> 105 % del VDOT. Foco en la economía y la velocidad neuromuscular.</li>
        </ul>

        <h3>3. Estructuración del plan y periodización</h3>
        <p>Los planes se configuran en un rango absoluto de 4 a 30 semanas, estructurándose de lunes a domingo, con la fecha de la competición ubicada en el último tramo de la semana final.</p>

        <h4>3.1 Fases del plan</h4>
        <ul>
            <li><b>Base:</b> ~30 % inicial de las semanas. Foco en volumen aeróbico, fuerza y adaptaciones estructurales.</li>
            <li><b>Construcción:</b> desarrollo de umbrales y potencia aeróbica mediante bloques de series y progresión de tempos.</li>
            <li><b>Pico:</b> últimas 3 semanas previas al descenso de cargas, maximizando la especificidad.</li>
            <li><b>Descarga (deload):</b> periodos de asimilación programados cada 4 semanas (o cada 3 en perfiles con historial de lesiones frecuentes).</li>
            <li><b>Afinamiento (taper):</b> reducción progresiva del volumen (1 a 2 semanas según la distancia objetivo) para garantizar la supercompensación sin pérdida de tono.</li>
            <li><b>Carrera B:</b> semana con una carrera de preparación (5K, 10K o media). Hace de descarga: los 3 días previos no llevan calidad (la víspera, descanso) y después solo hay rodajes suaves (2 días tras un 5K, 3 tras un 10K, 6 tras una media). Si la carrera es de 10K o más, sustituye a la tirada larga de esa semana. Con su tiempo, la app propone ajustar tus ritmos.</li>
        </ul>

        <h4>3.2 Distribución semanal de sesiones</h4>
        <ul>
            <li><b>Tirada larga:</b> ubicada en el día designado por el usuario (generalmente el fin de semana), constituye el núcleo de resistencia.</li>
            <li><b>Calidad principal (Q1):</b> asignada al día más distante de la tirada larga.</li>
            <li><b>Calidad secundaria (Q2 – tempo):</b> incorporada exclusivamente en esquemas de 4 o más días semanales, separada de las demás sesiones exigentes.</li>
            <li><b>Rodajes suaves:</b> rellenan el resto de la planificación, bajo el criterio de no concatenar estímulos de alta intensidad en días consecutivos.</li>
        </ul>

        <h3>4. Motor de evaluación y control de carga</h3>
        <p>El servicio de sincronización procesa las actividades importadas desde Garmin Connect para evaluar el rendimiento mediante métricas objetivas y subjetivas.</p>

        <h4>4.1 Carga de sesión y ratio agudo:crónico (ACWR)</h4>
        <ul>
            <li><b>Esfuerzo percibido por sesión (sRPE):</b>${M.loadFormula('Carga', 'Duración (min)')}</li>
            <li><b>Ratio de carga aguda a crónica (ACWR):</b> relaciona la carga acumulada en los últimos 7 días con la media de las últimas 4 semanas.
                <ul>
                    <li><i>Zona óptima:</i> ${M.acwrOptimal(l)}.</li>
                    <li><i>Zona de precaución / alto riesgo:</i> ${M.acwrAbove(l, '1.3')}.</li>
                </ul>
            </li>
        </ul>

        <h4>4.2 Eficiencia aeróbica</h4>
        <p>Se calcula como la relación entre la velocidad y la frecuencia cardíaca media (${M.hrRange('FC')}) en sesiones de baja intensidad, con una media móvil de 5 sesiones para identificar adaptaciones cardiovasculares.</p>

        <h3>5. Bucle de adaptación automática</h3>
        <p>Cada 2 semanas, el motor ejecuta un análisis de cumplimiento y estado físico para proponer modificaciones paramétricas (factor de volumen y VDOT).</p>

        <h4>5.1 Matriz de modificación del volumen</h4>
        ${helpTable(['Indicador de estado', 'Acción sobre el factor de volumen', 'Modificación estructural'], [
            ['Presencia de molestias físicas', `Multiplicador ${M.times(l, '0.90')}`, 'Conversión inmediata de la semana actual a <b>descarga</b>'],
            [`Muy cansado o cumplimiento ${M.below(60)}`, `Multiplicador ${M.times(l, '0.85')}`, 'Ninguna'],
            [`Cansado, molestias leves o cumplimiento ${M.below(80)}`, `Multiplicador ${M.times(l, '0.93')}`, 'Ninguna'],
            [`${M.acwrAbove(l, '1.5')} (independientemente del estado)`, `Reducción forzosa de al menos ${M.percent(10)}`, 'Ninguna'],
            ['Estado óptimo con factor previo reducido', `Incremento gradual ${M.plus(l, '0.05')} (tope ${M.value(l, '1.0')})`, 'Ninguna'],
        ])}
        <p class="help-note">Nota: el factor de volumen global se restringe estrictamente a un rango operacional de ${M.value(l, '0.70')} a ${M.value(l, '1.00')}, lo que asegura que el plan nunca supere la carga establecida originalmente en la fase de diseño.</p>

        <h3>6. Integración con el reloj Garmin</h3>
        <ul>
            <li><b>Ventana de sincronización:</b> se envían únicamente los entrenamientos de los <b>próximos 10 días</b> (ventana móvil), para no saturar el dispositivo y permitir flexibilidad ante los ajustes del motor.</li>
            <li><b>Estructura por bloques:</b> los entrenamientos se transmiten a través de Garmin Connect segmentados en fases explícitas (calentamiento, bloques de trabajo con alertas de rango de ritmo, recuperaciones y vuelta a la calma).</li>
        </ul>`;
    },

    en: () => {
        const M = HelpMath;
        const l = 'en';
        return `
        <p class="help-lead">This guide describes the logic architecture, physiological models and adaptation rules implemented in the app.</p>

        <h3>1. Architecture and system overview</h3>
        <p>The system builds individual running plans through a structured algorithmic approach:</p>
        <ul>
            <li><b>Base model:</b> pace-based training derived from Jack Daniels and Jimmy Gilbert's VDOT formulas.</li>
            <li><b>Periodization:</b> macro- and microcycles with base, build, peak, deload and <i>taper</i> phases.</li>
            <li><b>Load distribution:</b> follows the principle of polarized intensity (roughly the 80/20 model).</li>
            <li><b>Adaptive loop:</b> automated periodic reviews based on Garmin Connect telemetry and the runner's subjective feedback (RPE, fatigue, discomfort).</li>
        </ul>

        <h3>2. Physiological basis: the VDOT model</h3>
        <p>The engine estimates effective aerobic capacity by combining running economy (oxygen cost as a function of speed) with fatigue as a function of effort duration, based on the work of Jack Daniels and Jimmy Gilbert.</p>

        <h4>2.1 Equations</h4>
        <p>Given a reference result run at speed ${M.v} (meters per minute):</p>
        <ol>
            <li><b>Oxygen cost (${M.vo2}):</b>${M.vo2Formula(l)}</li>
            <li><b>Sustainable fraction of maximum</b> for a duration ${M.t} (minutes):${M.pctFormula(l)}</li>
            <li><b>VDOT value:</b>${M.vdotFormula(l)}</li>
        </ol>

        <h4>2.2 Intensity zones</h4>
        <p>From the VDOT, five training paces are derived by inverting the oxygen-cost curve at specific percentages of total capacity:</p>
        <ul>
            <li><b>E (Easy):</b> 62% – 72% of VDOT. Recovery and aerobic base.</li>
            <li><b>M (Marathon):</b> 82% of VDOT. Race-specific pace for long distances.</li>
            <li><b>T (Threshold):</b> 88% of VDOT. Raises the lactate threshold.</li>
            <li><b>I (Intervals):</b> 98% of VDOT. Direct VO₂max stimulus.</li>
            <li><b>R (Repetitions):</b> 105% of VDOT. Economy and neuromuscular speed.</li>
        </ul>

        <h3>3. Plan structure and periodization</h3>
        <p>Plans last between 4 and 30 weeks. Weeks run Monday to Sunday, and the race falls in the last week.</p>

        <h4>3.1 Plan phases</h4>
        <ul>
            <li><b>Base:</b> first ~30% of the weeks. Focus on aerobic volume, strength and structural adaptation.</li>
            <li><b>Build:</b> develops threshold and aerobic power through interval blocks and progressive tempo runs.</li>
            <li><b>Peak:</b> the last 3 weeks before the load comes down, with maximum specificity.</li>
            <li><b>Deload:</b> recovery weeks scheduled every 4 weeks (every 3 for runners with frequent injuries).</li>
            <li><b>Taper:</b> progressive volume reduction (1 to 2 weeks depending on the target distance) to reach supercompensation without losing sharpness.</li>
            <li><b>Tune-up race:</b> a week with a preparation race (5K, 10K or half). It works as a recovery week: no quality in the 3 days before (rest the day before) and only easy runs afterwards (2 days after a 5K, 3 after a 10K, 6 after a half). A race of 10K or longer replaces that week's long run. The app uses your time to suggest updating your paces.</li>
        </ul>

        <h4>3.2 Weekly session layout</h4>
        <ul>
            <li><b>Long run:</b> on the day you choose (usually the weekend); the core of endurance work.</li>
            <li><b>Main quality session (Q1):</b> placed on the day furthest from the long run.</li>
            <li><b>Secondary quality session (Q2 – tempo):</b> added only when you run 4 or more days a week, kept apart from the other hard sessions.</li>
            <li><b>Easy runs:</b> fill the rest of the week, so that hard sessions never fall on consecutive days.</li>
        </ul>

        <h3>4. Evaluation engine and load control</h3>
        <p>The sync service processes the activities imported from Garmin Connect and evaluates performance with objective and subjective metrics.</p>

        <h4>4.1 Session load and acute:chronic workload ratio (ACWR)</h4>
        <ul>
            <li><b>Session RPE (sRPE):</b>${M.loadFormula('Load', 'Duration (min)')}</li>
            <li><b>Acute:chronic workload ratio (ACWR):</b> compares the load of the last 7 days with the weekly average of the last 4 weeks.
                <ul>
                    <li><i>Optimal zone:</i> ${M.acwrOptimal(l)}.</li>
                    <li><i>Caution / high-risk zone:</i> ${M.acwrAbove(l, '1.3')}.</li>
                </ul>
            </li>
        </ul>

        <h4>4.2 Aerobic efficiency</h4>
        <p>Computed as speed relative to average heart rate (${M.hrRange('HR')}) in low-intensity sessions, using a 5-session moving average to reveal cardiovascular adaptations.</p>

        <h3>5. Automatic adaptation loop</h3>
        <p>Every 2 weeks, the engine analyzes compliance and physical state to propose parameter changes (volume factor and VDOT).</p>

        <h4>5.1 Volume adjustment matrix</h4>
        ${helpTable(['Condition', 'Volume factor action', 'Structural change'], [
            ['Physical discomfort reported', `Multiplier ${M.times(l, '0.90')}`, 'Current week becomes a <b>deload</b> week immediately'],
            [`Very tired or compliance ${M.below(60)}`, `Multiplier ${M.times(l, '0.85')}`, 'None'],
            [`Tired, mild discomfort or compliance ${M.below(80)}`, `Multiplier ${M.times(l, '0.93')}`, 'None'],
            [`${M.acwrAbove(l, '1.5')} (regardless of how you feel)`, `Forced reduction of at least ${M.percent(10)}`, 'None'],
            ['All good with a previously reduced factor', `Gradual increase ${M.plus(l, '0.05')} (capped at ${M.value(l, '1.0')})`, 'None'],
        ])}
        <p class="help-note">Note: the overall volume factor is strictly limited to the range ${M.value(l, '0.70')} to ${M.value(l, '1.00')}, so the plan never exceeds the load it was originally designed with.</p>

        <h3>6. Garmin watch integration</h3>
        <ul>
            <li><b>Sync window:</b> only the workouts for the <b>next 10 days</b> (rolling window) are sent, to avoid cluttering the device and to leave room for the engine's adjustments.</li>
            <li><b>Structured steps:</b> workouts are sent through Garmin Connect split into explicit steps (warm-up, work blocks with pace-range alerts, recoveries and cool-down).</li>
        </ul>`;
    },
};

function helpHtml(lang) {
    return `<article class="help">${(HELP[lang] || HELP.es)()}</article>`;
}
