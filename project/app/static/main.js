$(document).ready(function() {
    $(".cancel_session").on("click", function() {
        id=this.id
        user_id=this.name

        $.ajax({
            url: '/cancel-booking',
            type: 'POST',
            data: JSON.stringify({booking_id : id}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                $('#' + id).remove() // Removes the session card from the dashboard
                location.reload();
            },
            error: function(error){
                console.log(error);
            }
        })
    })
    
    $(".btn_day").on("click", function() {
        // this is a test button to display functionality of the get-slots AJAX call
        console.log("AJAX button clicked")
        // for now default weekday to monday - in reality weekday would be known from which calendar slot was pressed
        var date = new Date(this.name);
        var weekday = date.getDay();

        console.log("Name is: " + weekday)
        var sessions;

        $.ajax({
            url: '/get-slots',
            type: 'POST',
            data: JSON.stringify({weekday: weekday, year: date.getFullYear(), month: date.getMonth(), day: date.getDate()}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                // list sessions in a div to show that it works
                $("#sessions").text("")
                for (let i = 0; i < response.response.length; i++) {
                    console.log(response.response[i]);
                    console.log(response.response[i].session_name);

                    $("#sessions").append('Name: ' + response.response[i].session_name + '<br>Location: ' + response.response[i].location + '<br> Time: ' + response.response[i].time + '<br><hr>')
                }
            },
            error: function(error){
                console.log(error);
            }
        })
    });

    $("#btn_monday").on("click", function() {
        // this is a test button to display functionality of the get-slots AJAX call
        console.log("AJAX button clicked")
        // for now default weekday to monday - in reality weekday would be known from which calendar slot was pressed
        var weekday = 'monday';
        var sessions;

        $.ajax({
            url: '/get-slots',
            type: 'POST',
            data: JSON.stringify({weekday: weekday}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                // list sessions in a div to show that it works
                $("#sessions").text("")
                for (let i = 0; i < response.response.length; i++) {
                    console.log(response.response[i]);
                    console.log(response.response[i].session_name);
                    $("#sessions").append(response.response[i].session_name + '<br>')
                }
            },
            error: function(error){
                console.log(error);
            }
        })
    });

    $("#btn_book").on("click", function() {
        // this is a test button to display functionality of the book-slot AJAX call
        console.log("Book button clicked")
        // default slot id to 1 - in reality this is known by which booking button we click
        var slot_id = 1
        // default account id to 1 - we need a way to know which user pressed the button (maybe we can know this in routes.py)
        var account_id = 1
        // we would also provide a date here for the AJAX, but this would be obtained from the currently selected calander day
        // for now this is a hardcoded date in routes.py
        var date = 0

        // now we have all the data we need we can make the AJAX call
        $.ajax({
            url: '/book-slot',
            type: 'POST',
            data: JSON.stringify({slot_id: slot_id, account_id: account_id, date: date}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                // list sessions in a div to show that it works
                if (response.status == 'OK') {
                    console.log("Booked slot " + slot_id);
                } else {
                    console.log("Error! " + response.message);
                }
            },
            error: function(error){
                console.log(error);
            }
        })
    })

    function buildTable(response) {
        // build the table on the management page based on a response dictionary containing:
        // - name: a database table name
        // - data: a dictionary of table data
        let tbl_name = response.response['name'] ?? null
        let tbl_data = response.response['data'] ?? [null]
        let table = $('#mgmt-table');

        if (tbl_data[0] == null) {
            // don't show anything for an empty response or table_data
            table.html("No data");
            console.log("No data!")
            return;
        }

        // clear table
        table.html("");

        // get the keys from the table data - these are our table headers
        let keys = Object.keys(tbl_data[0]);
        let tr = "<tr>"
        for (let i = 0; i < keys.length; i++) {
            if (keys[i] == 'location') {
                // hardcoded removal of location id since we don't want the id and name as two fields
                // not very good, but not too bad - fixable later
                // also done later for each data row
                continue
            }
            // add the header to our row
            tr += "<th>" + keys[i] + "</th>"
        }
        // add button column as an extra empty header before adding in our row
        tr += "<th></th>"
        tr += "</tr>"
        table.append(tr);

        // add a row for each response data item
        for (let i = 0; i < tbl_data.length; i++) {
            let current_response = tbl_data[i];
            tr = "<tr>"
            for (let j = 0; j < keys.length; j++) {
                let response_item = current_response[keys[j]]
                if (keys[j] === 'location') {
                    // hardcoded location id removal (mentioned earlier)
                    continue
                }
                tr += "<td>"+ response_item +"</td>"
            }
            // add in an edit button to the end with id equal to the row's id, and the name equal to the table name
            tr += "<td>" + "<button class='btn_modal btn btn-primary' id=" + current_response['id'] + " name=" + tbl_name + ">Edit</button>" + "</td>"
            tr += "</tr>"
            table.append(tr);
        }
        // update the add button's name to the appropriate table
        $('#btn_add_modal').attr('name', tbl_name);
    }

    $('#btn_users').on("click", function() {
        // when the user button is clicked, run an ajax call for the users and build the table
        $.ajax({
            url: '/get-users',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: buildTable,
            error: function (error) {
                console.log(error);
            }
        })
    })

    $('#btn_calendar_slots').on("click", function() {
        // when the session button is clicked, run an ajax call for the sessions and build the table
        $.ajax({
            url: '/get-calendar_slots',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: buildTable,
            error: function (error) {
                console.log(error);
            }
        })
    })

    $('#btn_sessions').on("click", function() {
        // when the session button is clicked, run an ajax call for the sessions and build the table
        $.ajax({
            url: '/get-sessions',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: buildTable,
            error: function (error) {
                console.log(error);
            }
        })
    })

    $('#btn_locations').on("click", function() {
        // when the location button is clicked, run an ajax call for the locations and build the table
        $.ajax({
            url: '/get-locations',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: buildTable,
            error: function (error) {
                console.log(error);
            }
        })
    })

    $('#btn_discounts').on("click", function() {
        // when the discount button is clicked, run an ajax call for the discounts and build the table
        $.ajax({
            url: '/get-discounts',
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: buildTable,
            error: function (error) {
                console.log(error);
            }
        })
    })

    // default to no filter
    let filter_by = "none"

    $('input[type=radio][name=filter]').change(function() {
        console.log("filter changed!")
        filter_by = this.value
        let filter_div = $("#filter-selects")

        if (filter_by === "none") {
            filter_div.empty()
            // $("#btn-update-graph").trigger()
            return
        }

        let select_html = '<select class="form-select" id="select-filter" name="'+ filter_by +'">'

        $.ajax({
            url: '/get-' + filter_by,
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            async: false,
            success: function(response) {
                console.log(response)
                let response_items = response.response.data
                for (let i = 0; i < response_items.length; i++) {
                    console.log("Looking at item:")
                    let item = response_items[i]
                    console.log(item)
                    select_html += '<option value=' + item.id + '>' + item.name + '</option>'
                }
                select_html += '</select>'
            },
            error: function (error) {
                console.log(error);
            }
        })

        filter_div.html(select_html)
    });

});

$(document).on('click', '#btn-update-graph', function() {
    console.log("updating!")
    let select_filter = $("#select-filter")
    let table_name = select_filter.attr("name")
    let row_id = select_filter.val()

    console.log(table_name)
    console.log(row_id)

    $.ajax({
        url: '/update-graph',
        type: 'POST',
        data: JSON.stringify({table_name: table_name, row_id: row_id}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        // async: false,
        success: function(response) {
            console.log(response)
            let weekly_revenue = response.response.weekly_revenue
            let new_url = response.response.graph_url + "#" + new Date().getTime();

            console.log(new_url)
            $("#txt-sales-figure").html(weekly_revenue)
            $("#img-graph").attr("src", new_url)
            // deal with the response here - we get back a weekly revenue figure and an image link
        },
        error: function (error) {
            console.log(error);
        }
    })

})

$(document).on('click','.btn_modal', function(){
    // when the edit button on the management table is clicked, show the appropriate modal
    let tbl_name = this.name ?? null
    let tbl_id = this.id ?? null
    let modal = $('#mdl_' + tbl_name)
    modal.modal('show');
    // work out the correct ajax call from the button clicked
    let url = '/get-' + tbl_name
    let form = $('#form_' + tbl_name)
    if (this.id === 'btn_add_modal') {
        // clear the form here
        let form_groups = form.children('.form-group')
        form_groups.each(function(){
            // grab all inputs in the form group
            let input = $(this).find(':input')
            // clear each input except the confirmation
            if (input.attr("name") !== "submit") {
                input.val("");
            }
        });
        return
    }
    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify({id: tbl_id}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(response) {
            // get the first data item - only one should have been retrieved
            let row = response.response.data[0] ?? null
            if (!row) {
                return
            }
            for (let key in row) {
                // for each value in the row, find and update the value in the field
                let field = modal.find('#' + key)
                field.val(row[key]);
            }
        },
        error: function (error) {
            console.log(error);
        }
    })
});



$(document).on('click', '.date_today', function() {
    // grab and display sessions for calendar

    // get a date object from the calendar
    var date = new Date(this.getAttribute("name"));
    var weekday = date.getDay();

    // grab the filters
    let select_filter = $("#select-filter")
    let table_name = select_filter.attr("name")
    let row_id = select_filter.val()
    console.log("Showing table name and row ID to filter by")
    console.log(table_name)
    console.log(row_id)

    console.log("Name is: " + weekday);
    var sessions;

    $.ajax({
        url: '/get-slots',
        type: 'POST',
        data: JSON.stringify({weekday: weekday, year: date.getFullYear(), month: date.getMonth(), day: date.getDate(), table_name: table_name, row_id: row_id}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(response) {
            // list sessions in a div to show that it works
            $("#sessions").text("")
            for (let i = 0; i < response.response.length; i++) {
                const today = new Date()
                const todaym1 = new Date(today)
                todaym1.setDate(todaym1.getDate() - 1)
                if (date >= todaym1) {
                    console.log(response.response[i]);
                    console.log(response.response[i].session_name);

                    if (response.response[i].available == true) {
                        $("#sessions").append('<span>\
                        <div class="row flex-row flex-nowrap mt-2 pb-4 pt-2">\
                        <div class="col-12">\
                        <div class="card card-body card-block-calendar border border-info">\
                        <h5 class="card-title">' + response.response[i].session_name + '</h5>\
                        <h6 class="card-subtitle mb-2 text-muted">' + response.response[i].time + '</h6>\
                        <h7 class="card-subtitle mb-2 text-muted">' + response.response[i].location + '</h7>\
                        <h7 class="card-subtitle mb-2 text-info">Price: £' + response.response[i].price + '</h7>\
                        <h7 class="card-subtitle mb-3 text-success">Available</h7>\
                        <button id="' + response.response[i].id + '" class="btn_book align-self-end btn btn-sm btn-info mt-n5 mr-n1">Book</button>\
                        </div>\
                        </div>\
                        </span>'
                        )
                    } else {
                        $("#sessions").append('<span>\
                        <div class="row flex-row flex-nowrap mt-2 pb-4 pt-2">\
                        <div class="col-12">\
                        <div class="card card-body card-block-calendar border border-info">\
                        <h5 class="card-title">' + response.response[i].session_name + '</h5>\
                        <h6 class="card-subtitle mb-2 text-muted">' + response.response[i].time + '</h6>\
                        <h7 class="card-subtitle mb-2 text-muted">' + response.response[i].location + '</h7>\
                        <h7 class="card-subtitle mb-2 text-info">Price: £' + response.response[i].price + '</h7>\
                        <h7 class="card-subtitle mb-3 text-danger">Unavailable</h7>\
                        <button id="' + response.response[i].id + '" class="btn_book align-self-end btn btn-sm btn-secondary disabled mt-n5 mr-n1">Book</button>\
                        </div>\
                        </div>\
                        </span>'
                        )
                    }
                }
            }
        },
        error: function(error){
            console.log(error);
        }
    })
});

$(document).on('click', '.btn_book', function() {
    // this is a test button to display functionality of the book-slot AJAX call
    console.log("Book button clicked")

    // default slot id to 1 - in reality this is known by which booking button we click
    var slot_id = this.id

    // default account id to 1 - we need a way to know which user pressed the button (maybe we can know this in routes.py)
    var account_id = user_id
    
    // we would also provide a date here for the AJAX, but this would be obtained from the currently selected calander day
    // for now this is a hardcoded date in routes.py
    var date = document.querySelector(".date_today").getAttribute("name")

    var has_membership = false

    $.ajax({
        url: '/get-users',
        type: 'POST',
        data: JSON.stringify({id: account_id}),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        async: false,
        success: function(response) {
            let path = location.pathname.split('/').slice(-2)[0]
            has_membership=response.response.data[0].has_membership
            console.log(response)
            console.log(has_membership)
            if (has_membership == "Yes") {
                has_membership = true
            }
            if (has_membership == "No") {
                has_membership = false
            }
            if (path == "employee") {
                has_membership = true
            }
            console.log(has_membership)
        },
        error: function(error){
            console.log(error);
        }
    })

    console.log(has_membership)
    if (has_membership == true) {
        // now we have all the data we need we can make the AJAX call
        $.ajax({
            url: '/book-slot',
            type: 'POST',
            data: JSON.stringify({slot_id: slot_id, account_id: account_id, date: date}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {
                // list sessions in a div to show that it works
                if (response.status == 'OK') {
                    console.log("Booked slot " + slot_id);
                    location.reload();
                } else {
                    console.log("Error! " + response.message);
                }
            },
            error: function (error) {
                console.log(error);
            }
        })
    }
    console.log(has_membership)
    if (has_membership == false) {
        window.location.href = "/booking_nm/"+String(slot_id)+"/"+String(date);
        // Simulate an HTTP redirect:
        window.location.replace("/booking_nm/"+String(slot_id)+"/"+String(date));
    }
});

$(document).ready(function() {
    // select the users table by default on opening the management page
   $("#btn_users").trigger('click');
});