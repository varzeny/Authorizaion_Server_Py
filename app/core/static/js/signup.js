// signup.js

const PAGE = {
    panel:{},
    init:function(){
        // 패널들
        this.panel["seq0"] = document.getElementById("seq-0");
        this.panel["seq1"] = document.getElementById("seq-1");
        this.panel["seq2"] = document.getElementById("seq-2");
        this.panel["seq3"] = document.getElementById("seq-3");
        this.panel["seq4"] = document.getElementById("seq-4");
        this.changePanel("seq1");

        // 이벤트들
        document.addEventListener("submit", async function(event){
            if(event.target.classList.contains("form-seq")){
                event.preventDefault();

                PAGE.changePanel("seq0");
                
                let form = event.target;
                let formData = new FormData(form);
                try{
                    const resp = await fetch(form.action, {
                        method:"POST",
                        body:formData
                    });

                    if(!resp.ok){ throw new Error("서버에서 응답 없음") }

                    const respData = await resp.text();
                    console.log(respData);
                    PAGE.changePanel(respData);
                    
                }catch(error){
                    console.error("폼 제출 오류", error);
                    alert("something wrong. please retry signup sequence.");
                    window.location.reload();
                }
            }
        });
    },
    changePanel:function(name){
        Object.keys(this.panel).forEach(key => {
            this.panel[key].style.display = "none";
        });
        this.panel[name].style.display = "flex";
    }
}


document.addEventListener("DOMContentLoaded", init);


async function init() {
    // 페이지 태그들
    PAGE.init();


    console.log("로딩 완료");
}