function deleteContact(elem,pk,name) {
    if (confirm('Are you sure you want to remove ' + name + '?')) {
        $(elem).parents('tr').remove();
        $.post('../contacts/' + pk + '/delete/', function(data) {});
    }
}

function editContact(elem, pk) {
    overlay_loading_panel($(elem).parents('tr'));
    $(elem).parents('tr').load('../contacts/' + pk + '/edit/', '', function () {
        $('#div_panel_loading').hide();    
    });
}

function newContact(elem) {
    $(elem).parents('tr').load('../contacts/add/');
}

function submitForm(elem, action, resultDiv) {
    form = $(elem).parents("form");
    form_data = form.serializeArray();
    resultDiv.load(action, form_data);
}
