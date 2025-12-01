function validateRegister() {
    let n = document.getElementById("name").value;
    let e = document.getElementById("email").value;
    let p = document.getElementById("password").value;

    if(n=="" || e=="" || p==""){
        alert("All fields are required!");
        return false;
    }
    return true;
}
