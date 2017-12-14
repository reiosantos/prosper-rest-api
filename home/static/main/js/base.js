

/*
*
* splitters and sticky tables
*
* div sections
 *
 * for the pages
*
* defined here below
*
* */

$("#top-div table").stickyTableHeaders({
    //scrollableArea: $("#top-div"),
    //fixedOffset: 0,
});
$('#main-div1').enhsplitter({
    minSize: 100,
    position: '20%',
    vertical: false,
});
$('#bottom-div').enhsplitter({
    minSize: 100,
    position: '70%',
});

/*
*
* input types settings
*
* defined below
*
* including date, select
*
* and text inputs
*
* and investment update field(select investment)
*
* */
var selected_investment = $('.investment-selection').attr('readonly', true).val();
var selected_loan = $('.loan-selection').attr('readonly', true).val();

$("form").find("select[name='user']").val(SELECTED_USER).change();

function set_picker() {

    $("input.date-input").datetimepicker({
        changeMonth: true,
        changeYear: true,
        showOtherMonths: true,
        dateFormat: 'yy-mm-dd',
        timeFormat: 'HH:mm:ss',
        showMonthAfterYear: true,
        maxDate: new Date(),
        //showTimezone: true,
        defaultTime: new Date(),
        maxTime: 'now',
        timezone: '+0300',
        dynamic: true,
        showButtonPanel: true,
        beforeShowDay : function (date) {
            var dayOfWeek = date.getDay (); // 0 : Sunday, 1 : Monday, ...
            if (dayOfWeek === 0) return [false];
            else return [true];
        }
    });
    $('input[type="number"]')
        .attr('min',0).attr('step',1)
        .keyup(function (e) {
            if($(this).val() < 0 ){
                alert('negaitive values not allowed');
                $(this).val(0).focus()
            }
        });

    $('.investment-selection').on('change', function (e) {
        $(this).val(selected_investment).change()
    });
     $('.loan-selection').on('change', function (e) {
        $(this).val(selected_loan).change()
    })
}

set_picker();

/*
*
* slider for investment update
*
* is defined below
*
* */

if (default_slider === undefined ){
    default_slider = 0;
}

$("#valuestop").html(default_slider+"%");

$("input[name='project_rating']").val(default_slider);

$("div#slider").slider({
    min: 0,
    max: 100,
    range:'min',
    value: default_slider,
    animate: true,
    slide: function (event, ui) {
        var value = ui.value;
        var stop_el = $("#valuestop");
        stop_el.html(value+"%");
        if (value < 2){
            stop_el.html("100%");
        }

        myColor = get_color(value);

        $('#slider .ui-slider-range').css('background-color', myColor);
        $('#slider .ui-state-default, .ui-widget-content .ui-state-default').css('background-color', myColor);

        $("input[name='project_rating']").val(value);
    },
});

c = get_color(parseInt(default_slider));

$('#slider .ui-slider-range').css('background-color', c);
$('#slider .ui-state-default, .ui-widget-content .ui-state-default').css('background-color', c);

/* this function returns
 *
 * color of the slider
 *
 * depending on current slider value
 *
 * */
function get_color(value) {

    if (value < 25){
        return '#FF544A' //red-ish
    }
    if (value < 50){
        return 'orange'
    }
    if (value < 75){
        return '#FFF063' //yellowish
    }
    return '#37E030' //green-ish

}

/*
*
* these triggers or events
*
* below handle clicks and
*
* actions for tables in top div
*
* and lists of items in the right div
*
* */

$(".users_list li").click(function () {
    var account_id = $(this).attr("data");
    if(account_id !== undefined && account_id){
        get_user_object(account_id)
    }
});
$("#user-table tr").click(function () {
    var account_id = $(this).find('td:eq(0)').attr("data");
    if(account_id !== undefined && account_id){
        get_user_object(account_id)
    }
});
$("#contribution-table tr").click(function () {
    var slip_url = $(this).find('td:eq(-1)').attr("data");

    var id = $(this).find('td:eq(0)').attr("data");
    if(id !== undefined && id){
        get_contrib_object(id)
    }
    if(slip_url !== '' && slip_url !== null){
        $("#preview").attr('src', MEDIA_URL+slip_url)
    }
});
$("#investment-table tr, #loan-table tr, .right-li-links li, " +
    "li.ref, .dashboard-tables tr").click(function () {
    var link = $(this).data("href");
    if (link === undefined){
        return false
    }
    window.location = link
});


/*
*
* image preview
*
* settings here
*
* */

$("input[name='photo']").change(function () {
    preview_image(this)
});

/*
*
* function called to
*
* make preview
*
* */

function preview_image(input) {
    if(input.files && input.files[0]){
        var reader = new FileReader();
        reader.onload = function (e) {
            $("#user_preview").attr('src',e.target.result)
        };
        reader.readAsDataURL(input.files[0])
    }
}

/*
*
* auto filling forms
*
* including contrbution
*
* fields are changed
*
* */

$('.admin_contribution_form input[name="deposit"], ' +
    '.admin_contribution_form input[name="penalty"]')
    .keyup(function (event) {
        var deposit = $('.admin_contribution_form input[name="deposit"]').val();
        var penalt = $('.admin_contribution_form input[name="penalty"]').val();
        $('.admin_contribution_form input[name="total"]').val(deposit-penalt)
});
/*
*
* Function that auto fills loan form
*
* */
$('.admin_loan_form input[name="loan_amount"], ' +
    '.admin_loan_form input[name="loan_duration"], ' +
    '.admin_loan_form input[name="sur_charge"]')
    .keyup(function (event) {

        if($(this).val() < 0 || !$(this).val().match(/\d+(\.\d{0,2})?/)){
            return false
        }

        var rate = parseFloat($('.admin_interest_form input[name="interest"]').val());
        var duration = parseFloat($('.admin_loan_form input[name="loan_duration"]').val());
        var loan_amount = parseFloat($('.admin_loan_form input[name="loan_amount"]').val());
        var paid = parseFloat($('.admin_loan_form input[name="amount_paid"]').val());
        var surcharge = parseFloat($('.admin_loan_form input[name="sur_charge"]').val());

        var r = 0;
        if(duration <= 2){
            r = rate/100
        }else{
            r = (rate+((duration-2)*10))/100
        }

        var interest = loan_amount*r;
        var total_amount = loan_amount+interest;
        var balance = total_amount-paid;
        var sub_total = paid + surcharge;
        var profit = 0;

        if(paid >= total_amount){
            profit = (paid - loan_amount)+surcharge
        }

        $('.admin_loan_form input[name="loan_interest"]').val(interest.toFixed(1));
        $('.admin_loan_form input[name="total_amount"]').val(total_amount.toFixed(1));
        $('.admin_loan_form input[name="outstanding_balance"]').val(balance.toFixed(1));
        $('.admin_loan_form input[name="profit_earned"]').val(profit.toFixed(1));
        $('.admin_loan_form input[name="sub_total"]').val(sub_total.toFixed(1))
});

/*
*
* this function gets
*
* stored cookies needed
*
* to make ajax calls to the server
*
* */

function get_cookie(name) {
    var cookie_value = null;
    if(document.cookie && document.cookie != ''){
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++){
            var cookie = $.trim(cookies[i]);
            if (cookie.substring(0,name.length+1)==(name+'=')){
                cookie_value = decodeURIComponent(cookie.substring(name.length+1));
                break
            }
        }
    }
    return cookie_value
}

/*
*
* Function that sends
*
* ajax request to retrieve user object
*
* */

function get_user_object(acc_id) {

    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: 'ajax/',
        data: {id: acc_id,},
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken",get_cookie('csrftoken'))
        },
        success: function (data) {
            fill_user_form(data)
        },
        error: function(jqXHR, status, error){
            console.log(status+"----")
        },
    })
}

/*
*
* Function that sends
*
* ajax request to retrieve
*
* contribution base on id object
*
* */

function get_contrib_object(acc_id) {

    $.ajax({
        type: 'POST',
        dataType: 'json',
        data: {id: acc_id,},
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken",get_cookie('csrftoken'))
        },
        success: function (data) {
            fill_contrib_form(data)
        },
        error: function(jqXHR, status, error){
            console.log(status+"----")
        },
    })
}

/*
*
* Function that populates user
*
* form with data from server
*
* parsed by get_user_object()
*
* */

function fill_user_form(data) {

    $('#right-div .label-success').css('display','none');
    $('#right-div .label-danger').css('display','none');

    var form = $(".admin_user_form");
    $(form).find("input[name='account_id']").val(data['account_id']);
    $(form).find("input[name='first_name']").val(data['first_name']);
    $(form).find("input[name='last_name']").val(data['last_name']);
    $(form).find("input[name='address']").val(data['address']);
    $(form).find("input[name='email']").val(data['email']);
    $(form).find("input[name='contact']").val(data['contact']);
    if (data['is_staff']){
        $(form).find("input[name='is_staff']").prop('checked', true)
    }else{
        $(form).find("input[name='is_staff']").prop('checked', false)
    }

    $("#user_preview").attr('src',MEDIA_URL+data['photo']);

    $(form).find("input[name='username']").val(data['username']);
    $(form).find("input[name='password']").val(data['password']).attr('readonly', true);
    $(form).find("input[name='user_type']").each(function () {
        if($(this).val() === data['user_type']){
            $(this).prop('checked', true)
        }
    });
    if (data['is_superuser']){
        $(form).find("input[name='is_superuser']").prop('checked', true)
    }else{
        $(form).find("input[name='is_superuser']").prop('checked', false)
    }
    $(form).find("select[name='user_status']").val(data['user_status']).change();
    $(form).find("input[name='user_permissions']").val(Object.keys(data['user_permissions'])).change()
}


/*
*
* Function that populates contribution
*
* form with data from server
*
* parsed by get_contrib_object()
*
* */

function fill_contrib_form(data) {

    if(!data){
        alert('Failed to retrieve information');
        return
    }
    $('#right-div .label-success').css('display','none');
    $('#right-div .label-danger').css('display','none');

    var form = $(".admin_contribution_form");

    $(form).find("select[name='user']").val(data['account_id']).change();
    $(form).find("input[name='deposit']").val(data['deposit']);
    $(form).find("input[name='penalty']").val(data['penalty']);
    $(form).find("input[name='total']").val(data['total']);
    $(form).find("input[name='contribution_date']").val(data['contribution_date']);
    $(form).find("input[name='hidden_contribution']").val(data['id']);

    if(!can_modify){
        $(form).find("input[name='submit']").attr('disabled', true);
        $(form).find("#warn").html("you don't have permissions to modify or add a contribution")
    }
}


/*
*
* Function makes ajax
*
* request to server for search
*
* typed in search box
*
* */

function make_search(event) {
    s_b = $("#make_search_input");
    var v = s_b.val();
    var tab = s_b.attr("data");
    $.ajax({
        type: 'POST',
        dataType: 'json',
        data: {table: tab, search: v},
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken",get_cookie('csrftoken'))
        },
        success: function (data) {
            if (data){
                if (tab === "contributions"){
                    contrib_table(data)
                }
                if(tab === "users"){
                    user_table(data)
                }
                if(tab === "investments"){
                    invest_table(data)
                }
                 if(tab === "loans"){
                    loan_table(data)
                }
            }
        },
        error: function(jqXHR, status, error){
            console.log("----"+ error)
        },
    })
}

/*
*
* Function that regenerates
*
* user table in top-div with
*
* data parsed by make_search()
*
* */

function user_table(data) {
    var table = $("#user-table");
    var temp = '';
    for (record in data){

        if(data[record]['user_status'] !== "approved"){
            temp += "<tr class='not_approved' >"
        }else{
            temp += "<tr>"
        }
        temp += "<td data='"+data[record]['account_id']+"' >"+data[record]['account_id']+"</td>" +
            "<td>"+data[record]['first_name']+"</td>" +
            "<td>"+data[record]['last_name']+"</td>" +
            "<td>"+data[record]['email']+"</td>" +
            "<td>"+data[record]['contact']+"</td>" +
            "<td>"+data[record]['address']+"</td>" +
            "<td>"+data[record]['username']+"</td>" +
            "<td>"+data[record]['user_type']+"</td>" +
            "<td>"+data[record]['user_status']+"</td>" +
            "<td>"+data[record]['date_joined']+"</td>" +
            "<td>"+data[record]['is_superuser']+"</td>" +
            "</tr>"
    }
    table.html(temp);

    $("#user-table tr").click(function () {
        var account_id = $(this).find('td:eq(0)').attr("data");
        get_user_object(account_id)
    })
}

/*
*
* Function that regenerates
*
* contribution table in top-div with
*
* data parsed by make_search()
*
* */

function contrib_table(data) {
    var table = $("#contribution-table");
    var temp = '';
    for (record in data){
        temp += "<tr>" +
            "<td data='"+ data[record]['id'] +"'>"+data[record]['account_id']+"</td>" +
            "<td>"+data[record]['first_name']+"</td>" +
            "<td>"+data[record]['last_name']+"</td>" +
            "<td>"+data[record]['deposit']+"</td>" +
            "<td>"+data[record]['penalty']+"</td>" +
            "<td>"+data[record]['total']+"</td>" +
            "<td>"+data[record]['contribution_date']+"</td>" +
            "<td data='"+data[record]['deposit_slip']+"' >" +data[record]['deposit_slip'] +"</td>" +
            "</tr>"
    }
    table.html(temp);

    $("#contribution-table tr").click(function () {
        var account_id = $(this).find('td:eq(-1)').attr("data");
        var id = $(this).find('td:eq(0)').attr("data");
        get_contrib_object(id);

        if(account_id !== '' && account_id !== null){
            $("#preview").attr('src', MEDIA_URL+account_id)
        }
    })
}

/*
*
* Function that regenerates
*
* investment table in top-div with
*
* data parsed by make_search()
*
* */

function invest_table(data) {
    var table = $("#investment-table");
    var temp = '';
    for (record in data){

        if(i && i !== undefined){
            if(data[record]['status'] === 'cancelled'){
                temp += "<tr data-href='"+ url + data[record]['project_id']+"' class='not_approved' >"
            }else{
                temp += "<tr data-href='"+ url + data[record]['project_id']+"' >"
            }
        }else{
             if(data[record]['status'] === 'cancelled'){
                temp += "<tr class='not_approved' >"
            }else{
                temp += "<tr>"
            }
        }
        temp +=
            "<td data='"+data[record]['project_id']+"' >"+data[record]['manager']+"</td>" +
            "<td>"+data[record]['project_name']+"</td>" +
            "<td>"+data[record]['start_date']+"</td>" +
            "<td>"+data[record]['age']+"</td>" +
            "<td>"+data[record]['capital']+"</td>" +
            "<td>"+data[record]['interest']+"</td>" +
            "<td>"+data[record]['loss']+"</td>" +
            "<td>"+data[record]['status']+"</td>" +
            "<td>"+data[record]['rating']+"</td>" +
            "</tr>"
    }
    table.html(temp);

    $("#investment-table tr").click(function () {
        window.location = $(this).data("href");
    })
}

/*
*
* Function that regenerates
*
* loan table in top-div with
*
* data parsed by make_search()
*
* */

function loan_table(data) {
    var table = $("#loan-table");
    var temp = '';
    for (record in data){

        if(data[record]['status'] === 'cancelled'){
            temp += "<tr data-href='"+ url + data[record]['id']+"' class='not_approved' >"
        }else if(data[record]['status'] === 'completed'){
            temp += "<tr data-href='"+ url + data[record]['id']+"' class='completed' >"
        }else{
             temp += "<tr data-href='"+ url + data[record]['id']+"' >"
        }
        temp +=
            "<td>"+data[record]['user']+"</td>" +
            "<td>"+data[record]['loan_date']+"</td>" +
            "<td>"+data[record]['loan_duration']+"</td>" +
            "<td>"+data[record]['amount']+"</td>" +
            "<td>"+data[record]['interest']+"</td>" +
            "<td>"+data[record]['total']+"</td>" +
            "<td>"+data[record]['paid']+"</td>" +
            "<td>"+data[record]['balance']+"</td>" +
            "<td>"+data[record]['profit']+"</td>" +
            "<td>"+data[record]['status']+"</td>" +
            "</tr>"
    }
    table.html(temp);

    $("#loan-table tr").click(function () {
        var link = $(this).data("href");
        if (link === undefined){
            return false
        }
        window.location = link
    })
}


/*
*
* events for formsets
*
* handed here
*
* */
$('.form-set td:has(ul.errorlist)').addClass('has-error');
