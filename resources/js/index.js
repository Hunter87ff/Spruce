/*hunter bot*/
var element = document.body;
var button = document.getElementById('tbutton')
var count = 0;


   function theme(){
   element.classList.toggle("dark-mode");
    if(count == 0){
    count = 1;
    button.innerHTML="dark";
    }else{
      count = 1;
      count = 0;
      button.innerHTML="light"
    }
}