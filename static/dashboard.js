async function loadStatus() {

    const response = await fetch("/api/status");
    const data = await response.json();

    const container = document.getElementById("machineCards");
    container.innerHTML = "";

    data.forEach(machine => {

        let css = "stopped";

        if (machine.state === "RUNNING")
            css = "running";

        if (machine.state === "FAULT")
            css = "fault";

        const col = document.createElement("div");
        col.className = "col-12 col-lg-4 col-xxl-3 mb-3";

        col.innerHTML = `
            <div class="card ${css} text-white shadow">

                <div class="card-body">

                    <div class="d-flex justify-content-between align-items-center">
                        <h2>${machine.machine}</h2>
                        <h2>${machine.state}</h2>
                    </div>

                    <hr>

                    <div class="row text-center">

                        <div class="col">
                            <h2>${machine.shift1}</h2>
                            <small>1st shift</small>
                        </div>

                        <div class="col">
                            <h2>${machine.shift2}</h2>
                            <small>2nd shift</small>
                        </div>

                        <div class="col">
                            <h2>${machine.pieces}</h2>
                            <small>Total</small>
                        </div>

                    </div>

                </div>

            </div>
        `;

        container.appendChild(col);

    });

}

async function refresh() {
    try {
        await loadStatus();
    } catch (err) {
        console.error(err);
    }
}

refresh();

setInterval(refresh, 2000);

function updateDateTime() {
    const now = new Date();

    const options = {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric"
    };

    const date = now.toLocaleDateString("ro-RO", options);
    const time = now.toLocaleTimeString("ro-RO");

    document.getElementById("datetime").innerHTML =
        `${date} | ${time}`;
}

updateDateTime();
setInterval(updateDateTime, 1000);
