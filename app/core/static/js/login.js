// login.js




document.addEventListener("DOMContentLoaded", init);

async function init() {

    document.addEventListener("submit", async function(event) {
        if(event.target.classList.contains("login-form")){
            event.preventDefault();

            try{
                const resp = await fetch(event.target.action, {
                    method:"POST",
                    body:new FormData(event.target)
                });

                if(!resp.ok){ throw new Error("서버에서 응답 없음") }

                console.log("ok");


            }catch(error){
                console.error("폼 제출 오류", error);
                alert("something wrong. please retry login");
            }
        }
    })


    console.log("로딩 완료");
}