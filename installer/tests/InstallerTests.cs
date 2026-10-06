using System;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Drawing;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

internal static class InstallerTests
{
    const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
    static Type install = typeof(Setup).GetNestedType("InstallForm", BindingFlags.NonPublic);
    static string root = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "cases");
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern SafeFileHandle CreateFile(string path, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    static object Field(object o,string name) { return o.GetType().GetField(name, Private).GetValue(o); }
    static void Check(bool condition,string name) { if (!condition) throw new Exception(name); Console.WriteLine("PASS " + name); }
    static Form NewForm(string target) {
        Form f = (Form)Activator.CreateInstance(install, Private, null, new object[]{target,false,1024L,new Bitmap(10,10)},null);
        IntPtr handle = f.Handle; return f;
    }
    static void Payload(bool unsafePath) {
        string path = Path.ChangeExtension(Assembly.GetExecutingAssembly().Location, ".dat");
        using (FileStream file = File.Create(path))
        using (ZipArchive zip = new ZipArchive(file,ZipArchiveMode.Create)) {
            using (StreamWriter writer = new StreamWriter(zip.CreateEntry(unsafePath ? "../escape.txt" : "nested/app.txt").Open())) writer.Write("new payload");
            zip.CreateEntry("empty/");
        }
    }
    static void NoStaging(string target) {
        Check(Directory.GetDirectories(root,Path.GetFileName(target)+".__staging_*").Length == 0,"staging cleaned");
    }
    [STAThread] static int Main() {
        try {
            root = Path.Combine(root, Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            using (Form f = NewForm(Path.Combine(root,"ui"))) {
                f.StartPosition = FormStartPosition.Manual;
                f.Location = new Point(-10000,-10000);
                f.Show();
                ComboBox languages = (ComboBox)Field(f,"languageSelector");
                Label space = (Label)Field(f,"spaceInfo");
                Label message = (Label)Field(f,"message");
                for(int i=0;i<4;i++) {
                    languages.SelectedIndex=i;
                    int needed=space.GetPreferredSize(new Size(space.Width,0)).Height;
                    Check(space.Height>=needed && message.Top>=space.Bottom+8,"language "+i+" wrapped space fits");
                    using(Bitmap image=new Bitmap(f.Width,f.Height)) {
                        f.DrawToBitmap(image,new Rectangle(0,0,image.Width,image.Height));
                        image.Save(Path.Combine(root,"layout-"+i+".png"));
                    }
                }
            }
            Type uninstall=typeof(Setup).GetNestedType("UninstallConfirmForm",BindingFlags.NonPublic);
            using(Form f=(Form)Activator.CreateInstance(uninstall,true)) {
                PictureBox icon=null; ComboBox language=null;
                foreach(Control control in f.Controls) { if(control is PictureBox) icon=(PictureBox)control; if(control is ComboBox) language=(ComboBox)control; }
                Check(icon!=null && icon.Image!=null && language.Left-icon.Right==6,"uninstall icon and 6px language gap");
            }
            MethodInfo retry=install.GetMethod("RetryFileOperation",BindingFlags.Static|BindingFlags.NonPublic);
            int attempts=0;
            retry.Invoke(null,new object[]{(Action)delegate{ attempts++; if(attempts<3) throw new IOException("temporary lock"); }});
            Check(attempts==3,"temporary lock retries");
            Payload(false);
            string target=Path.Combine(root,"success");
            Directory.CreateDirectory(target); File.WriteAllText(Path.Combine(target,"old.txt"),"old");
            using(Form f=NewForm(target)) install.GetMethod("Install",Private).Invoke(f,null);
            Check(File.ReadAllText(Path.Combine(target,"nested/app.txt"))=="new payload" && !File.Exists(Path.Combine(target,"old.txt")),"upgrade installs new payload");
            NoStaging(target);
            Check(Directory.GetDirectories(root,"success.__previous_*").Length==0,"success removes backup");
            target=Path.Combine(root,"copy");
            string stage=target+".__staging_test";
            Directory.CreateDirectory(Path.Combine(stage,"nested")); Directory.CreateDirectory(Path.Combine(stage,"empty"));
            File.WriteAllText(Path.Combine(stage,"nested/app.txt"),"copy payload");
            using(Form f=NewForm(target))
            using(SafeFileHandle locked=CreateFile(stage,0,3,IntPtr.Zero,3,0x02000000,IntPtr.Zero)) {
                object[] args={stage,false};
                install.GetMethod("CopyStagedInstallation",Private).Invoke(f,args);
                Check((bool)args[1] && File.ReadAllText(Path.Combine(target,"nested/app.txt"))=="copy payload" && Directory.Exists(Path.Combine(target,"empty")),"copy fallback preserves files and empty directories");
            }
            install.GetMethod("DeleteTree",BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,new object[]{stage});
            Check(!Directory.Exists(stage),"fallback staging cleanup");
            Payload(true);
            target=Path.Combine(root,"unsafe");
            Directory.CreateDirectory(target); File.WriteAllText(Path.Combine(target,"old.txt"),"old");
            using(Form f=NewForm(target)) install.GetMethod("Install",Private).Invoke(f,null);
            Check(File.ReadAllText(Path.Combine(target,"old.txt"))=="old" && !File.Exists(Path.Combine(root,"escape.txt")),"invalid archive preserves old installation");
            NoStaging(target);
            Payload(false);
            target=Path.Combine(root,"cancel");
            using(Form f=NewForm(target)) {
                install.GetField("cancelRequested",Private).SetValue(f,true);
                install.GetMethod("Install",Private).Invoke(f,null);
            }
            Check(!Directory.Exists(target),"cancel leaves no installation"); NoStaging(target);
            Console.WriteLine("ALL CHECKS PASSED"); return 0;
        } catch(Exception ex) { Console.WriteLine(ex); return 1; }
    }
}
