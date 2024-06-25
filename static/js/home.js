const btn = document.querySelector("#burger");
const cross = document.querySelector("#cross");
const dropMenu = document.querySelector("#menu");
const noAnimation = document.querySelectorAll(".noAnimation");
const upload = document.querySelector("#imageUpload");
const image_input = document.querySelector("#file-input");
const buttons = document.querySelectorAll("button");

btn.addEventListener("click", () => {
  dropMenu.classList.remove("w-0");
  dropMenu.classList.remove("hidden");
  dropMenu.classList.add("w-[95%]");
  btn.classList.add("hidden");
  cross.classList.remove("hidden");
  document.body.style.overflow = "hidden";
});

cross.addEventListener("click", () => {
  dropMenu.classList.add("w-0");
  dropMenu.classList.add("hidden");
  dropMenu.classList.remove("w-[95%]");
  btn.classList.remove("hidden");
  cross.classList.add("hidden");
  document.body.style.overflow = "auto";
});

const observer = new IntersectionObserver((sect) => {
  sect.forEach((ele) => {
    if (ele.isIntersecting) {
      ele.target.classList.add("animateScroll");
    }
  });
});

noAnimation.forEach((ele) => observer.observe(ele));

if (upload) {
  upload.addEventListener("click", () => {
    image_input.click();
  });
}

if (image_input) {
  image_input.onchange = function () {
    document.getElementById("upload-form").submit();
  };
}
