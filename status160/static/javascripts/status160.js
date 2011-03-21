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
    rowelem = $(elem).parents('tr')
    rowelem.after('<tr></tr>')
    rowelem.next().load('../contacts/add');
    $('#add_contact_anchor_row').hide();
}

function submitForm(elem, action, resultDiv) {
    form = $(elem).parents("form");
    form_data = form.serializeArray();
    resultDiv.load(action, form_data);
}
