// Global variable to create a new date object
const current_date = new Date();

// Function to hold calendar code so that it can be rendered on changing months
const render_calendar = () => {
    current_date.setDate(1); // Sets the start date for days to be added to the calendar

    const month_days = document.querySelector(".days");

    // Getting previous days on the calendar
    const last_day = new Date(current_date.getFullYear(), current_date.getMonth() + 1, 0).getDate();
    const previous_last_day = new Date(current_date.getFullYear(), current_date.getMonth(), 0).getDate();

    // Indexing first and last days
    const index_first_day = current_date.getDay();
    const index_last_day = new Date(current_date.getFullYear(), current_date.getMonth() + 1, 0).getDay();

    // How many of the next month's days are to be shown on the current month's calendar space
    const next_days = 7 - index_last_day - 1;

    // List of months
    const months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    // Changing header information with the current month and date
    document.querySelector(".selected_date h2").innerHTML = months[current_date.getMonth()];
    document.querySelector(".selected_date p").innerHTML = new Date().toDateString();

    let days = "";

    // Getting the final days of the previous month to be shown on the calendar
    for(let x = index_first_day; x > 0; x--) {
        days += `<div class="previous_date">${previous_last_day - x + 1}</div>`;
    }

    // Displaying the days of the selected month on the calendar
    for(let i = 1; i <= last_day; i++) {
        if (i === new Date().getDate() && current_date.getMonth() === new Date().getMonth()) {
            days += `<div class="date_today" id=calendar${i} onclick=selectDate(${i})>${i}</div>`;
        } else {
            days += `<div id=calendar${i} onclick=selectDate(${i})>${i}</div>`;
        }
    }

    // Getting the days of the next month to be displayed on the calendar
    for(let j = 1; j <= next_days; j++) {
        days += `<div class="following_date">${j}</div>`
    }

    // Updating calendar with days for that month
    month_days.innerHTML = days;
}

// Function to give functionaluty to the previous month button
document.querySelector(".left_button").addEventListener('click', () => {
    current_date.setMonth(current_date.getMonth() - 1);
    render_calendar();
});

// Function to give functionaluty to the next month button
document.querySelector(".right_button").addEventListener('click', () => {
    current_date.setMonth(current_date.getMonth() + 1);
    render_calendar();
});

// Rendering the calendar on page load
render_calendar();

// Function for selecting a date on the calendar
function selectDate(date) {
    // Removes previously highlighted box
    var dateExists = document.getElementsByClassName("date_today");
    if (dateExists.length > 0) {
        document.querySelector(".date_today").classList.remove("date_today")
    }

    // Adds the date_today tag to the selected date, which applies styling to that date
    var element = document.getElementById("calendar" + date)
    element.classList.add("date_today")

    // Getting the date, converting it to the correct string format and adding it to a name attribute on the html page
    var dateString = current_date.getFullYear().toString() + "-" + (current_date.getMonth()+1).toString() + "-" + date;
    document.getElementById("calendar" + date).setAttribute("name", dateString);
    var dateString = current_date.toISOString().substring(0,10);
}