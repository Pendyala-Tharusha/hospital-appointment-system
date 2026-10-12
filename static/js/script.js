document.addEventListener(
    "DOMContentLoaded",
    function () {

        const dateInput =
            document.getElementById(
                "appointmentDate"
            );

        if (dateInput) {

            const today =
                new Date()
                    .toISOString()
                    .split("T")[0];

            dateInput.min = today;
        }

    }
);


function confirmCancellation() {

    return confirm(
        "Are you sure you want to cancel this appointment?"
    );

}


setTimeout(function () {

    const alerts =
        document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        alert.style.display = "none";

    });

}, 5000);