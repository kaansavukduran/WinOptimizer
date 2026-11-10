using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace AionHardware {
    public sealed class Gpu {
        public string Name;
        public uint VendorId;
        public uint DeviceId;
        public ulong DedicatedVideoBytes;
        public ulong DedicatedSystemBytes;
        public ulong SharedSystemBytes;
        public bool Software;
        public bool Remote;
    }
    public static class Dxgi {
        [StructLayout(LayoutKind.Sequential)] struct Luid { public uint Low; public int High; }
        [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct Description {
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string Name;
            public uint VendorId, DeviceId, SubsystemId, Revision;
            public UIntPtr DedicatedVideo, DedicatedSystem, SharedSystem;
            public Luid AdapterLuid;
            public uint Flags;
        }
        [DllImport("dxgi.dll", CallingConvention=CallingConvention.StdCall)]
        static extern int CreateDXGIFactory1(ref Guid id, out IntPtr factory);
        [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int Enumerate(IntPtr self, uint index, out IntPtr adapter);
        [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int Describe(IntPtr self, out Description description);
        static Delegate Function(IntPtr instance, int slot, Type type) {
            return Marshal.GetDelegateForFunctionPointer(Marshal.ReadIntPtr(Marshal.ReadIntPtr(instance), slot*IntPtr.Size), type);
        }
        public static Gpu[] Read() {
            IntPtr factory=IntPtr.Zero;
            Guid id=new Guid("770aae78-f26f-4dba-a829-253c83d1b387");
            Marshal.ThrowExceptionForHR(CreateDXGIFactory1(ref id, out factory));
            try {
                var enumerate=(Enumerate)Function(factory,12,typeof(Enumerate));
                var result=new List<Gpu>();
                for(uint index=0;index<128;index++) {
                    IntPtr adapter;
                    int code=enumerate(factory,index,out adapter);
                    if(unchecked((uint)code)==0x887A0002)break;
                    Marshal.ThrowExceptionForHR(code);
                    try {
                        Description d;
                        Marshal.ThrowExceptionForHR(((Describe)Function(adapter,10,typeof(Describe)))(adapter,out d));
                        result.Add(new Gpu { Name=d.Name.TrimEnd('\0'), VendorId=d.VendorId, DeviceId=d.DeviceId,
                            DedicatedVideoBytes=d.DedicatedVideo.ToUInt64(), DedicatedSystemBytes=d.DedicatedSystem.ToUInt64(),
                            SharedSystemBytes=d.SharedSystem.ToUInt64(), Software=(d.Flags&2)!=0, Remote=(d.Flags&1)!=0 });
                    } finally { if(adapter!=IntPtr.Zero)Marshal.Release(adapter); }
                }
                return result.ToArray();
            } finally { if(factory!=IntPtr.Zero)Marshal.Release(factory); }
        }
    }
}
