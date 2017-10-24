$(document).ready(function () {
    // Code adapted from http://djangosnippets.org/snippets/1389/
    function updateElementIndex(el, prefix, ndx) {

        var id_regex = new RegExp('(' + prefix + '-\\d+-)');
        var replacement = prefix + '-' + ndx + '-';
        if ($(el).attr("for"))
            $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    }

    function deleteForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        if (formCount > 1) {
            // Delete the item/form
            $(btn).parents('.form-set').remove();
            var forms = $('.form-set'); // Get all the forms
            // Update the total number of forms (1 less than before)
            $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
            var i = 0;
            // Go through the forms and set their indices, names and IDs
            for (formCount = forms.length; i < formCount; i++) {
                $(forms.get(i)).find('input, select, textarea').each(function () {
                    updateElementIndex(this, prefix, i);
                });
                //var replacement = '#id_'+prefix + '-' + (i) + '-id';
                //$(forms.get(i)).find(replacement).val((i+1))
            }
        } // End if
        else {
            alert("You have to enter at least one form!");
        }
        return false;
    }

    function addForm(btn, prefix) {
        var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        var formMax = parseInt($('#id_' + prefix + '-MAX_NUM_FORMS').val());
        // You can only submit a maximum of specified forms
        if (formCount < formMax) {
            // Clone a form (without event handlers) from the first form
            var row = $(".form-set:first").clone(false).get(0);
            v = $(".form-set:first").find('input[name="csrfmiddlewaretoken"]').val();

            /*v1 = $(".form-set:first").find('.investment-selection').val()
            v2 = $(".form-set:first").find('.loan-selection').val()*/

            // Insert it after the last form
            $(row).removeAttr('id').hide().insertAfter(".form-set:last").slideDown(300);

            // Remove the bits we don't want in the new row/form
            // e.g. error messages
            $(".errorlist", row).remove();
            $(row).children().removeClass("error");

            // Relabel or rename all the relevant bits
            $(row).find('input, select, textarea').each(function () {
                updateElementIndex(this, prefix, formCount);
                $(this).val("");
            });

            //var replacement = '#id_'+prefix + '-' + formCount + '-id';
            //$(row).find(replacement).val(formCount+1)
            $(row).find('input[name="csrfmiddlewaretoken"]').val(v);

            if (selected_investment !== undefined){
                $(row).find('.investment-selection').val(selected_investment).change()
            }
            if (selected_loan !== undefined){
               $(row).find('.loan-selection').val(selected_loan).change()
            }
            set_picker();

            // Add an event handler for the delete item/form link
            $(row).find(".delete").click(function () {
                if(confirm('Sure to Delete entry ?')){
                    return deleteForm(this, prefix);
                }
                return false
            });
            // Update the total form count
            $("#id_" + prefix + "-TOTAL_FORMS").val(formCount + 1);

        } // End if
        else {
            alert("Sorry, you can only enter a maximum of "+ formMax +" items.");
        }
        return false;
    }
    // Register the click event handlers
    $("#add").click(function () {
        return addForm(this, "form");
    });

    $(".delete").click(function () {
        if(confirm('Sure to Delete entry ?')){
            return deleteForm(this, "form");
        }
        return false
    });
});