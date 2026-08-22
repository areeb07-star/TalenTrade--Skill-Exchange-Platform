function attachSkillAutocomplete(inputId, listId){
  const inp = document.getElementById(inputId);
  const list = document.getElementById(listId);
  if(!inp || !list) return;
  inp.addEventListener("input", async ()=>{
    const q = inp.value.trim();
    if(!q){ list.innerHTML=""; return; }
    const res = await fetch(`/search_skill?q=${encodeURIComponent(q)}`);
    const skills = await res.json();
    list.innerHTML = "";
    skills.forEach(s=>{
      const li = document.createElement("li");
      li.textContent = s;
      li.onclick = ()=>{ inp.value = s; list.innerHTML=""; };
      list.appendChild(li);
    });
  });
}
