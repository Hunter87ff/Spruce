// https://github.com/hunter87ff
var theme = localStorage.getItem("theme")
if(theme == null){
    localStorage.setItem("theme", "light")
};
if(theme=="dark"){
    document.querySelector("body").classList.add("dark")
}else{
    document.querySelector("body").classList.remove("dark")
}
//document.querySelector("body").classList.toggle("dark");
var count = 0;
function theme_change(){
    if(count==0){
        document.querySelector("body").classList.add("dark")
        localStorage.setItem("theme", "dark")
        count=1;
    }else{
        document.querySelector("body").classList.remove("dark")
        localStorage.setItem("theme", "light")
        count=0;
    }
}
function menu_toggle(){
    var nav = document.querySelector(".nav")
    var sidebtn = document.querySelector("#menu-btn")
    var count = 0
    nav.classList.toggle('show');
    if(count==0){
        sidebtn.className= "fa-solid fa-xmark";
        count=1
    }else{
        count=0;
        sidebtn.className= "fa-solid fa-bars";
    }
}

function toggleMenu() {
    var menu = document.querySelector(".nav")
    var menuButton = document.querySelector('.menu-button');
    menuButton.classList.toggle('menu-open');
    menu.classList.toggle("show")
}

const observer = new IntersectionObserver((entries) =>{
    entries.forEach((entry)=>{
        if (entry.isIntersecting){
            entry.target.classList.add("show");
        }else{
            entry.target.classList.remove("show");
        }
    })
})
const hiddenelm = document.querySelectorAll(".type-con");
hiddenelm.forEach((el) => observer.observe(el));


function subscribe(){
    var inp = document.querySelector("#email");
    var sub = document.querySelector("#sub-btn");
    if(inp.value==""){
        alert("Please Enter A Valid Email")
    }else if(inp.value.includes("@") == false){
        alert("Please Enter A Valid Email")
    }else{
        console.log(this)
        sub.innerHTML = "Subscribed";
    }
};

function cont_touch(){
    var menu = document.querySelector(".nav");
    var menuButton = document.querySelector('.menu-button');
    var cont = document.querySelector(".cont");
    cont.addEventListener("click", function(){
        menuButton.classList.remove('menu-open');
        menu.classList.remove("show")
    });
}
cont_touch()

//const ldata = {"ping":"pong"};


$(document).ready(function() {
  $("#cform").submit(function(event) {
    event.preventDefault();
    var data = {
      "name": $("#name").val(),
      "email": $("#email").val(),
      "subject": $("#subject").val(),
      "desc": $("#desc").val()
    };
    $.post("/api/contact", data, function(response) {
      //console.log(response);
      document.querySelector("#card").style.display="none";
      var car = document.querySelector("#car")
      car.style.display = "block";
      if (response.success) {
        alert("Your message has been sent!");
      } else {
        // The request failed
        $("#error").removeClass("error--hidden");
      }
    });
  });
});


