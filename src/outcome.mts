export function hasIncompleteResult(result: {success?:boolean;failed?:number;conflicts?:number;items?:{success?:boolean}[]}|null|undefined):boolean {
  return result?.success===false || (result?.failed??0)>0 || (result?.conflicts??0)>0 || (Array.isArray(result?.items)&&result.items.some(item=>item.success===false));
}
