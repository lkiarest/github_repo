async function setModel(){
  const model=document.getElementById('modelInput').value;
  if(!model)return;
  await fetch('http://127.0.0.1:8000/config',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({openclaw_model:model})
  });
  alert('模型已切换为: '+model);
}
