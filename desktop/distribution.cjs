const path=require('node:path');
function distribution(packaged,env,local){
 const portable=!!(packaged&&env.PORTABLE_EXECUTABLE_DIR&&path.isAbsolute(env.PORTABLE_EXECUTABLE_DIR));
 return {portable,data:portable?path.join(env.PORTABLE_EXECUTABLE_DIR,'Data'):path.join(local,'WinOptimizer Aion')};
}
module.exports={distribution};
