// ============================================================
// SPIDEY HUD — FRONTEND CONTROLLER
// ============================================================

const $ = (id) => document.getElementById(id);

const state = {
    started: performance.now(),
    network: Array(80).fill(0)
};


// ============================================================
// CLOCK
// ============================================================

function updateClock() {

    const now = new Date();

    const time = now.toLocaleTimeString([], {
        hour12: false
    });

    $("topTime").textContent = time;
    $("bigTime").textContent = time;

    $("date").textContent =
        now.toLocaleDateString([], {
            weekday: "long",
            day: "2-digit",
            month: "long",
            year: "numeric"
        });
}

updateClock();

setInterval(updateClock, 1000);


// ============================================================
// SPIDEY STATE
// ============================================================

function setState(newState) {

    $("mainState").textContent =
        newState.split("").join(" ");

    $("voiceState").textContent =
        newState;


    let meter = 55;


    if (newState === "LISTENING") {
        meter = 92;
    }

    else if (newState === "THINKING") {
        meter = 76;
    }

    else if (newState === "SPEAKING") {
        meter = 88;
    }


    $("coreMeter").style.width =
        meter + "%";


    document.body.dataset.state =
        newState;
}


// ============================================================
// SYSTEM TELEMETRY
// ============================================================

function updateTelemetry() {

    /*
        These values are currently simulated.

        Later we will connect them to Python
        so the GUI receives real system data.
    */

    const cpu =
        Math.round(
            15 + Math.random() * 45
        );

    const ram =
        Math.round(
            35 + Math.random() * 30
        );

    const disk =
        Math.round(
            15 + Math.random() * 25
        );


    $("cpu").textContent =
        cpu + "%";

    $("ram").textContent =
        ram + "%";

    $("disk").textContent =
        disk + "%";


    $("cpuBar").style.width =
        cpu + "%";

    $("ramBar").style.width =
        ram + "%";

    $("diskBar").style.width =
        disk + "%";


    // Network

    const download =
        Math.round(
            Math.random() * 900
        );

    const upload =
        Math.round(
            Math.random() * 180
        );


    $("down").textContent =
        download;

    $("up").textContent =
        upload;


    state.network.push(
        Math.max(
            3,
            Math.min(
                55,
                download / 18
            )
        )
    );

    state.network.shift();


    drawNetwork();
}


updateTelemetry();

setInterval(
    updateTelemetry,
    1400
);


// ============================================================
// NETWORK GRAPH
// ============================================================

function drawNetwork() {

    const canvas =
        $("networkGraph");

    const ctx =
        canvas.getContext("2d");


    const rect =
        canvas.getBoundingClientRect();


    canvas.width =
        rect.width *
        devicePixelRatio;

    canvas.height =
        rect.height *
        devicePixelRatio;


    ctx.scale(
        devicePixelRatio,
        devicePixelRatio
    );


    const width =
        rect.width;

    const height =
        rect.height;


    ctx.clearRect(
        0,
        0,
        width,
        height
    );


    // Grid

    ctx.strokeStyle =
        "rgba(255,20,20,.10)";

    for (
        let y = 10;
        y < height;
        y += 20
    ) {

        ctx.beginPath();

        ctx.moveTo(
            0,
            y
        );

        ctx.lineTo(
            width,
            y
        );

        ctx.stroke();
    }


    // Graph

    ctx.strokeStyle =
        "#ff1717";

    ctx.lineWidth = 1.3;

    ctx.beginPath();


    state.network.forEach(
        (value, index) => {

            const x =
                index *
                (
                    width /
                    (state.network.length - 1)
                );


            const y =
                height -
                8 -
                value;


            if (index === 0) {

                ctx.moveTo(
                    x,
                    y
                );

            } else {

                ctx.lineTo(
                    x,
                    y
                );
            }
        }
    );


    ctx.stroke();
}


// ============================================================
// AUDIO WAVEFORM
// ============================================================

function animateWave() {

    const canvas =
        $("wave");

    const ctx =
        canvas.getContext("2d");


    const rect =
        canvas.getBoundingClientRect();


    canvas.width =
        rect.width *
        devicePixelRatio;

    canvas.height =
        rect.height *
        devicePixelRatio;


    ctx.scale(
        devicePixelRatio,
        devicePixelRatio
    );


    const width =
        rect.width;

    const height =
        rect.height;


    const time =
        performance.now() / 300;


    ctx.clearRect(
        0,
        0,
        width,
        height
    );


    ctx.strokeStyle =
        "#ff1717";

    ctx.lineWidth = 1.5;

    ctx.beginPath();


    for (
        let x = 0;
        x < width;
        x += 4
    ) {

        const envelope =
            Math.sin(
                Math.PI *
                x /
                width
            );


        const y =
            height / 2 +
            Math.sin(
                x * 0.09 +
                time * 2.5
            ) *
            7 *
            envelope;


        if (x === 0) {

            ctx.moveTo(
                x,
                y
            );

        } else {

            ctx.lineTo(
                x,
                y
            );
        }
    }


    ctx.stroke();


    requestAnimationFrame(
        animateWave
    );
}


animateWave();


// ============================================================
// UPTIME
// ============================================================

function updateUptime() {

    const seconds =
        Math.floor(
            (
                performance.now() -
                state.started
            ) / 1000
        );


    const hours =
        String(
            Math.floor(
                seconds / 3600
            )
        ).padStart(
            2,
            "0"
        );


    const minutes =
        String(
            Math.floor(
                (seconds % 3600) /
                60
            )
        ).padStart(
            2,
            "0"
        );


    const secs =
        String(
            seconds % 60
        ).padStart(
            2,
            "0"
        );


    $("uptime").textContent =
        `${hours}:${minutes}:${secs}`;
}


updateUptime();

setInterval(
    updateUptime,
    1000
);


// ============================================================
// FLOATING PARTICLES
// ============================================================

function createParticles() {

    const holder =
        $("particles");


    for (
        let i = 0;
        i < 45;
        i++
    ) {

        const particle =
            document.createElement(
                "span"
            );


        particle.className =
            "particle";


        particle.style.left =
            Math.random() *
            100 +
            "%";


        particle.style.top =
            Math.random() *
            100 +
            "%";


        particle.style.animationDuration =
            (
                7 +
                Math.random() * 15
            ) +
            "s";


        particle.style.animationDelay =
            (
                -Math.random() * 15
            ) +
            "s";


        holder.appendChild(
            particle
        );
    }
}


createParticles();


// ============================================================
// LOG SYSTEM
// ============================================================

function addLog(message) {

    const log =
        $("log");


    const row =
        document.createElement(
            "div"
        );


    row.className =
        "line";


    const time =
        new Date().toLocaleTimeString(
            [],
            {
                hour12: false
            }
        );


    row.innerHTML =
        `
        <span class="stamp">
            ${time}
        </span>
        ${message}
        `;


    log.appendChild(
        row
    );


    while (
        log.children.length >
        9
    ) {

        log.removeChild(
            log.firstChild
        );
    }


    log.scrollTop =
        log.scrollHeight;
}


// ============================================================
// QUICK COMMANDS
// ============================================================

document
    .querySelectorAll(".quick button")
    .forEach(
        (button) => {

            button.addEventListener(
                "click",
                () => {

                    const command =
                        button.dataset.command;


                    $("command").value =
                        command;


                    addLog(
                        "Command queued: " +
                        command
                    );
                }
            );
        }
    );


// ============================================================
// COMMAND INPUT
// ============================================================

$("command")
    .addEventListener(
        "keydown",
        (event) => {

            if (
                event.key !==
                "Enter"
            ) {
                return;
            }


            const command =
                $("command")
                .value
                .trim();


            if (!command) {
                return;
            }


            addLog(
                "Command received: " +
                command
            );


            setState(
                "THINKING"
            );


            setTimeout(
                () => {

                    setState(
                        "STANDBY"
                    );

                },
                1000
            );
        }
    );


// ============================================================
// INITIAL LOG
// ============================================================

addLog(
    "System initialized"
);

addLog(
    "Voice engine online"
);

addLog(
    "Core connection established"
);

addLog(
    "Wake phrase: Hey Spidey"
);

addLog(
    "SPIDEY standing by"
);


// ============================================================
// START STATE
// ============================================================

setState(
    "STANDBY"
);