function deleteContact(elem,link,name) {
    if (confirm('Are you sure you want to remove ' + name + '?')) {
        $(elem).parents('tr').remove();
        $.post(link, function(data) {});
    }
}

function editContact(elem, link) {
    overlay_loading_panel($(elem).parents('tr'));
    $(elem).parents('tr').load(link, '', function () {
        $('#div_panel_loading').hide();    
    });
}

function newContact(elem, link) {
    rowelem = $(elem).parents('tr')
    rowelem.after('<tr></tr>')
    rowelem.next().load(link);
    $('#add_contact_anchor_row').hide();
}

function submitForm(elem, action, resultDiv) {
    form = $(elem).parents("form");
    form_data = form.serializeArray();
    resultDiv.load(action, form_data);
}
