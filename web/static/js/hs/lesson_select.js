function select_on_change(n){
    document.getElementById('what_request').value = n.id
    document.forms[0].submit()
}