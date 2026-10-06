using System;
using System.IO;
using System.IO.Compression;
using System.Diagnostics;
using System.Drawing;
using System.Reflection;
using System.Windows.Forms;
using System.Collections.Generic;
using Microsoft.Win32;

internal static class Setup
{
    private const string Magic = "ARMAISET";
    private static readonly string AppVersion = GetAppVersion();
    private const string InstallPath = @"C:\Program Files\ArmAI\ImageEnhancer";
    private const string ProductKey = @"Software\Microsoft\Windows\CurrentVersion\Uninstall\ArmAIImageEnhancer";
    private const long ReserveBytes = 1000000000L;
    private static readonly Dictionary<string, string[]> Texts = new Dictionary<string, string[]>
    {
        { "ภาษา", new[] { "ภาษา", "Language", "语言", "Langue" } },
        { "ติดตั้ง ARM AI Image Enhancer V.", new[] { "ติดตั้ง ARM AI Image Enhancer V.", "Install ARM AI Image Enhancer V.", "安装 ARM AI Image Enhancer V.", "Installer ARM AI Image Enhancer V." } },
        { "โปรดตรวจสอบพื้นที่และรายละเอียดก่อนเริ่มติดตั้ง โปรแกรมจะติดตั้งลงใน C:\\Program Files\\ArmAI\\ImageEnhancer", new[] { "โปรดตรวจสอบพื้นที่และรายละเอียดก่อนเริ่มติดตั้ง โปรแกรมจะติดตั้งลงใน C:\\Program Files\\ArmAI\\ImageEnhancer", "Review the space and details before installing. The program will be installed to C:\\Program Files\\ArmAI\\ImageEnhancer", "请在安装前检查磁盘空间和详细信息。程序将安装到 C:\\Program Files\\ArmAI\\ImageEnhancer", "Vérifiez l’espace et les détails avant l’installation. Le programme sera installé dans C:\\Program Files\\ArmAI\\ImageEnhancer" } },
        { "ข้อมูลสำคัญ", new[] { "ข้อมูลสำคัญ\n• Windows 64-bit\n• AI Upscale: 2x / 4x / 8x (Real-ESRGAN)\n• Face Recovery: GFPGAN พร้อมโมเดลตรวจจับใบหน้า\n• Device: AUTO / CPU / NVIDIA GPU (CUDA)\n• การ์ดจอยี่ห้ออื่นประมวลผลด้วย CPU\n• รวมโมเดลและไฟล์ที่จำเป็นในตัวติดตั้ง\n• ใช้ NVIDIA GPU ต้องมีไดรเวอร์ที่รองรับ", "Important information\n• Windows 64-bit\n• AI Upscale: 2x / 4x / 8x (Real-ESRGAN)\n• Face Recovery: GFPGAN with face detection models\n• Device: AUTO / CPU / NVIDIA GPU (CUDA)\n• Other graphics cards use the CPU\n• Models and required files are included\n• NVIDIA GPU requires a supported driver", "重要信息\n• Windows 64 位\n• AI 放大：2x / 4x / 8x (Real-ESRGAN)\n• 人脸修复：GFPGAN 和人脸检测模型\n• 设备：AUTO / CPU / NVIDIA GPU (CUDA)\n• 其他显卡将使用 CPU 处理\n• 安装包包含模型和必要文件\n• 使用 NVIDIA GPU 需要兼容的驱动程序", "Informations importantes\n• Windows 64 bits\n• Agrandissement IA : 2x / 4x / 8x (Real-ESRGAN)\n• Visages : GFPGAN avec modèles de détection\n• Appareil : AUTO / CPU / NVIDIA GPU (CUDA)\n• Les autres cartes graphiques utilisent le CPU\n• Modèles et fichiers requis inclus\n• Un pilote compatible est requis pour NVIDIA GPU" } },
        { "พื้นที่ว่าง C: {0:N1} GB\nต้องเหลืออย่างน้อย {1:N1} GB เพื่อติดตั้งไฟล์โปรแกรมประมาณ {2:N1} GB พร้อมพื้นที่สำรอง 1 GB\nหากไฟล์ Setup อยู่บน C: ควรเตรียมพื้นที่ประมาณ {3:N1} GB ก่อนดาวน์โหลด (รวมไฟล์ติดตั้งราว {4:N1} GB)", new[] { "พื้นที่ว่าง C: {0:N1} GB\nต้องเหลืออย่างน้อย {1:N1} GB เพื่อติดตั้งไฟล์โปรแกรมประมาณ {2:N1} GB พร้อมพื้นที่สำรอง 1 GB\nหากไฟล์ Setup อยู่บน C: ควรเตรียมพื้นที่ประมาณ {3:N1} GB ก่อนดาวน์โหลด (รวมไฟล์ติดตั้งราว {4:N1} GB)", "Free space on C: {0:N1} GB\nAt least {1:N1} GB is needed to install about {2:N1} GB of program files plus 1 GB reserve\nIf Setup is on C:, allow about {3:N1} GB before downloading (including about {4:N1} GB of setup files)", "C: 可用空间：{0:N1} GB\n安装约 {2:N1} GB 的程序文件并预留 1 GB，至少需要 {1:N1} GB\n如果安装程序位于 C:，下载前请预留约 {3:N1} GB（安装文件约 {4:N1} GB）", "Espace libre sur C: {0:N1} Go\nAu moins {1:N1} Go sont nécessaires pour installer environ {2:N1} Go de fichiers et réserver 1 Go\nSi le programme d’installation se trouve sur C:, prévoyez environ {3:N1} Go avant le téléchargement (fichiers d’installation : {4:N1} Go)" } },
        { "ช่วยสนับสนุนการพัฒนาโปรแกรม\n5 บาท 10 บาท ได้หมดครับ", new[] { "ช่วยสนับสนุนการพัฒนาโปรแกรม\n5 บาท 10 บาท ได้หมดครับ", "Support the development\n5 or 10 baht, any amount is welcome", "欢迎支持程序开发\n5 或 10 泰铢都可以", "Soutenez le développement\n5 ou 10 bahts, tout montant est bienvenu" } },
        { "แล้วแต่ศรัทธา", new[] { "แล้วแต่ศรัทธา", "Whatever you feel like", "随心支持", "Selon votre envie" } },
        { "สแกน QR PromptPay เพื่อสนับสนุน", new[] { "สแกน QR PromptPay เพื่อสนับสนุน", "Scan the PromptPay QR code to support", "扫描 PromptPay 二维码以支持开发", "Scannez le QR PromptPay pour soutenir le projet" } },
        { "สร้างไอคอน ARM AI Image Enhancer บน Desktop", new[] { "สร้างไอคอน ARM AI Image Enhancer บน Desktop", "Create an ARM AI Image Enhancer desktop shortcut", "在桌面创建 ARM AI Image Enhancer 快捷方式", "Créer un raccourci ARM AI Image Enhancer sur le bureau" } },
        { "เปิดโปรแกรมหลังติดตั้งเสร็จ", new[] { "เปิดโปรแกรมหลังติดตั้งเสร็จ", "Launch the program after installation", "安装完成后启动程序", "Lancer le programme après l’installation" } },
        { "ติดตั้ง", new[] { "ติดตั้ง", "Install", "安装", "Installer" } },
        { "ยกเลิก", new[] { "ยกเลิก", "Cancel", "取消", "Annuler" } },
        { "ยืนยันยกเลิกการติดตั้งหรือไม่? ไฟล์ชั่วคราวจะถูกลบออก", new[] { "ยืนยันยกเลิกการติดตั้งหรือไม่? ไฟล์ชั่วคราวจะถูกลบออก", "Cancel installation? Temporary files will be removed.", "确定取消安装吗？临时文件将被删除。", "Annuler l’installation ? Les fichiers temporaires seront supprimés." } },
        { "การติดตั้งถูกยกเลิกและลบไฟล์ชั่วคราวแล้ว", new[] { "การติดตั้งถูกยกเลิกและลบไฟล์ชั่วคราวแล้ว", "Installation cancelled. Temporary files were removed.", "安装已取消，临时文件已删除。", "Installation annulée. Les fichiers temporaires ont été supprimés." } },
        { "ยกเลิกการติดตั้ง", new[] { "ยกเลิกการติดตั้ง", "Cancel installation", "取消安装", "Annuler l’installation" } },
        { "กำลังยกเลิกและลบไฟล์ชั่วคราว…", new[] { "กำลังยกเลิกและลบไฟล์ชั่วคราว…", "Cancelling and removing temporary files…", "正在取消并删除临时文件…", "Annulation et suppression des fichiers temporaires…" } },
        { "กำลังเตรียมติดตั้ง…", new[] { "กำลังเตรียมติดตั้ง…", "Preparing installation…", "正在准备安装…", "Préparation de l’installation…" } },
        { "กำลังติดตั้งไฟล์โปรแกรม… {0}%", new[] { "กำลังติดตั้งไฟล์โปรแกรม… {0}%", "Installing program files… {0}%", "正在安装程序文件… {0}%", "Installation des fichiers… {0}%" } },
        { "กำลังย้ายไฟล์จากโฟลเดอร์ชั่วคราว…", new[] { "กำลังย้ายไฟล์จากโฟลเดอร์ชั่วคราว…", "Moving files from the temporary folder…", "正在移动临时文件…", "Déplacement des fichiers temporaires…" } },
        { "กำลังคัดลอกไฟล์เข้าตำแหน่งติดตั้ง… {0}%", new[] { "กำลังคัดลอกไฟล์เข้าตำแหน่งติดตั้ง… {0}%", "Copying files to the install location… {0}%", "正在将文件复制到安装位置… {0}%", "Copie des fichiers vers l’emplacement d’installation… {0}%" } },
        { "ติดตั้งเสร็จแล้ว", new[] { "ติดตั้งเสร็จแล้ว", "Installation complete", "安装完成", "Installation terminée" } },
        { "ติดตั้ง ARM AI Image Enhancer เรียบร้อยแล้วที่:\n", new[] { "ติดตั้ง ARM AI Image Enhancer เรียบร้อยแล้วที่:\n", "ARM AI Image Enhancer was installed successfully at:\n", "ARM AI Image Enhancer 已成功安装到：\n", "ARM AI Image Enhancer a été installé avec succès dans :\n" } },
        { "ติดตั้งสำเร็จ", new[] { "ติดตั้งสำเร็จ", "Installation complete", "安装成功", "Installation réussie" } },
        { "ติดตั้งไม่สำเร็จ", new[] { "ติดตั้งไม่สำเร็จ", "Installation failed", "安装失败", "Échec de l’installation" } },
        { "ติดตั้งไม่สำเร็จ ระบบลบไฟล์ชั่วคราวและพยายามคืนไฟล์เดิมแล้ว\n\n", new[] { "ติดตั้งไม่สำเร็จ ระบบลบไฟล์ชั่วคราวและพยายามคืนไฟล์เดิมแล้ว\n\n", "Installation failed. Temporary files were removed and the previous installation was restored when possible.\n\n", "安装失败。已清理临时文件，并在可能的情况下恢复了原版本。\n\n", "Échec de l’installation. Les fichiers temporaires ont été supprimés et l’ancienne version restaurée si possible.\n\n" } },
        { "ยืนยันถอนการติดตั้ง ARM AI Image Enhancer หรือไม่?", new[] { "ยืนยันถอนการติดตั้ง ARM AI Image Enhancer หรือไม่?", "Do you want to uninstall ARM AI Image Enhancer?", "确定要卸载 ARM AI Image Enhancer 吗？", "Voulez-vous désinstaller ARM AI Image Enhancer ?" } },
        { "ลบการตั้งค่าและรายการล่าสุดของผู้ใช้นี้ด้วย", new[] { "ลบการตั้งค่าและรายการล่าสุดของผู้ใช้นี้ด้วย", "Also delete this user's settings and recent files", "同时删除此用户的设置和最近文件记录", "Supprimer aussi les paramètres et les fichiers récents de cet utilisateur" } },
        { "ถอนการติดตั้ง", new[] { "ถอนการติดตั้ง", "Uninstall", "卸载", "Désinstaller" } },
        { "ถอนการติดตั้ง ARM AI Image Enhancer", new[] { "ถอนการติดตั้ง ARM AI Image Enhancer", "Uninstall ARM AI Image Enhancer", "卸载 ARM AI Image Enhancer", "Désinstaller ARM AI Image Enhancer" } },
        { "คุณต้องการถอนการติดตั้ง ARM AI Image Enhancer หรือไม่?", new[] { "คุณต้องการถอนการติดตั้ง ARM AI Image Enhancer หรือไม่?", "Uninstall ARM AI Image Enhancer?", "要卸载 ARM AI Image Enhancer 吗？", "Désinstaller ARM AI Image Enhancer ?" } },
        { "ถอนการติดตั้งไม่สำเร็จ\n\n", new[] { "ถอนการติดตั้งไม่สำเร็จ\n\n", "Uninstall failed\n\n", "卸载失败\n\n", "Échec de la désinstallation\n\n" } },
        { "พื้นที่ C: ไม่เพียงพอ\nต้องการอย่างน้อย {0:N1} GB แต่เหลือ {1:N1} GB\nลบไฟล์ที่ไม่ใช้งานหรือเลือกติดตั้งภายหลังเมื่อเพิ่มพื้นที่แล้ว", new[] { "พื้นที่ C: ไม่เพียงพอ\nต้องการอย่างน้อย {0:N1} GB แต่เหลือ {1:N1} GB\nลบไฟล์ที่ไม่ใช้งานหรือเลือกติดตั้งภายหลังเมื่อเพิ่มพื้นที่แล้ว", "Not enough space on C:\nAt least {0:N1} GB is required, but only {1:N1} GB is free\nFree up space or try again after making more space", "C: 空间不足\n至少需要 {0:N1} GB，目前仅有 {1:N1} GB\n请释放空间后重试", "Espace insuffisant sur C:\nAu moins {0:N1} Go sont requis, mais seulement {1:N1} Go sont libres\nLibérez de l’espace puis réessayez" } },
        { "พื้นที่ไม่เพียงพอ", new[] { "พื้นที่ไม่เพียงพอ", "Insufficient space", "空间不足", "Espace insuffisant" } },
        { "ARM AI Image Enhancer", new[] { "ARM AI Image Enhancer", "ARM AI Image Enhancer", "ARM AI Image Enhancer", "ARM AI Image Enhancer" } },
    };

    private static string Translate(string thai, int language)
    {
        string[] values;
        return Texts.TryGetValue(thai, out values) ? values[Math.Max(0, Math.Min(3, language))] : thai;
    }

    private static void SetLocalized(Control control, string thai, int language)
    {
        control.Tag = thai;
        control.Text = Translate(thai, language);
    }

    private static void ApplyTranslations(Control parent, int language)
    {
        foreach (Control control in parent.Controls)
        {
            string key = control.Tag as string;
            if (key != null) control.Text = Translate(key, language);
            ApplyTranslations(control, language);
        }
    }

    private static string GetAppVersion()
    {
        Version version = Assembly.GetExecutingAssembly().GetName().Version;
        return version == null || version.Major == 0 ? "2.0.2" : version.ToString(3);
    }

    private sealed class RegistrationSnapshot
    {
        internal bool KeyExists;
        internal readonly Dictionary<string, object> Values = new Dictionary<string, object>(StringComparer.OrdinalIgnoreCase);
        internal readonly Dictionary<string, RegistryValueKind> Kinds = new Dictionary<string, RegistryValueKind>(StringComparer.OrdinalIgnoreCase);
        internal bool MenuDirectoryExisted;
        internal bool MenuShortcutExisted;
        internal byte[] MenuShortcut;
        internal bool DesktopShortcutExisted;
        internal byte[] DesktopShortcut;
        internal string MenuDirectory;
        internal string MenuShortcutPath;
        internal string DesktopShortcutPath;
    }

    [STAThread]
    private static void Main(string[] args)
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        if ((args.Length > 0 && args[0] == "--uninstall") ||
            String.Equals(Path.GetFileNameWithoutExtension(Application.ExecutablePath), "Uninstall", StringComparison.OrdinalIgnoreCase))
        {
            Uninstall();
            return;
        }

        string target = InstallPath;
        bool register = true;
        if (args.Length == 2 && args[0] == "--extract-to")
        {
            target = Path.GetFullPath(args[1]);
            register = false;
        }
        try
        {
            Application.Run(new StartupForm(target, register));
        }
        catch (Exception ex)
        {
            MessageBox.Show("ตัวติดตั้งอ่านข้อมูลไม่สำเร็จ\n\n" + ex.Message,
                "ARM AI Image Enhancer Setup", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private sealed class StartupForm : Form
    {
        private readonly string target;
        private readonly bool register;

        internal StartupForm(string targetPath, bool writeRegistration)
        {
            target = targetPath;
            register = writeRegistration;
            Text = "ARM AI Image Enhancer — Setup";
            Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(500, 132);
            Label title = new Label { Left = 20, Top = 16, Width = 460, Height = 28,
                Text = "ARM AI Image Enhancer V." + AppVersion, Font = new Font("Tahoma", 12, FontStyle.Bold), TextAlign = ContentAlignment.MiddleCenter };
            Label status = new Label { Left = 20, Top = 53, Width = 460, Height = 22,
                Text = "กำลังเตรียมไฟล์ติดตั้ง…", Font = new Font("Tahoma", 9), TextAlign = ContentAlignment.MiddleCenter };
            ProgressBar activity = new ProgressBar { Left = 20, Top = 84, Width = 460, Height = 18,
                Style = ProgressBarStyle.Marquee, MarqueeAnimationSpeed = 25 };
            Controls.Add(title);
            Controls.Add(status);
            Controls.Add(activity);
            Shown += delegate { System.Threading.ThreadPool.QueueUserWorkItem(delegate { LoadPayload(); }); };
        }

        private void LoadPayload()
        {
            try
            {
                long payloadBytes;
                Image qr;
                InspectPayload(out payloadBytes, out qr);
                BeginInvoke((Action)delegate
                {
                    Hide();
                    using (InstallForm form = new InstallForm(target, register, payloadBytes, qr)) form.ShowDialog();
                    Close();
                });
            }
            catch (Exception ex)
            {
                BeginInvoke((Action)delegate
                {
                    MessageBox.Show(this, "ตัวติดตั้งอ่านข้อมูลไม่สำเร็จ\n\n" + ex.Message,
                        "ARM AI Image Enhancer Setup", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    Close();
                });
            }
        }
    }

    private static void InspectPayload(out long payloadBytes, out Image qr)
    {
        payloadBytes = 0;
        qr = null;
        using (PayloadStream payload = new PayloadStream(Assembly.GetExecutingAssembly().Location))
        using (ZipArchive archive = new ZipArchive(payload.Content, ZipArchiveMode.Read, true))
        {
            foreach (ZipArchiveEntry entry in archive.Entries) payloadBytes += entry.Length;
            ZipArchiveEntry qrEntry = archive.GetEntry("_internal/assets/QR.jpg");
            if (qrEntry == null) throw new InvalidDataException("PromptPay QR image is missing from the setup payload.");
            using (Stream imageStream = qrEntry.Open())
            using (MemoryStream memory = new MemoryStream())
            {
                imageStream.CopyTo(memory);
                memory.Position = 0;
                using (Image decoded = Image.FromStream(memory)) qr = new Bitmap(decoded);
            }
        }
        if (payloadBytes <= 0 || qr == null) throw new InvalidDataException("The setup payload is incomplete.");
    }

    private sealed class PayloadStream : IDisposable
    {
        private readonly Stream source;
        internal readonly Stream Content;

        internal PayloadStream(string executablePath)
        {
            string sidecar = Path.Combine(Path.GetDirectoryName(executablePath),
                Path.GetFileNameWithoutExtension(executablePath) + ".dat");
            string firstPart = sidecar + ".001";
            if (File.Exists(firstPart))
            {
                List<string> parts = new List<string>();
                for (int index = 1; ; index++)
                {
                    string part = sidecar + "." + index.ToString("D3");
                    if (!File.Exists(part)) break;
                    parts.Add(part);
                }
                source = new SplitFilesStream(parts);
                Content = source;
            }
            else if (File.Exists(sidecar))
            {
                source = File.OpenRead(sidecar);
                Content = source;
            }
            else
            {
                source = File.OpenRead(executablePath);
                long start, length;
                ReadPayloadBounds(source, out start, out length);
                Content = new SegmentStream(source, start, length);
            }
        }

        public void Dispose()
        {
            source.Dispose();
        }
    }

    private sealed class SplitFilesStream : Stream
    {
        private readonly FileStream[] files;
        private readonly long[] starts;
        private readonly long length;
        private long position;

        internal SplitFilesStream(List<string> paths)
        {
            if (paths == null || paths.Count == 0) throw new InvalidDataException("Setup data parts are missing.");
            files = new FileStream[paths.Count];
            starts = new long[paths.Count];
            try
            {
                for (int i = 0; i < paths.Count; i++)
                {
                    starts[i] = length;
                    files[i] = File.OpenRead(paths[i]);
                    length += files[i].Length;
                }
            }
            catch
            {
                Dispose();
                throw;
            }
        }

        public override bool CanRead { get { return true; } }
        public override bool CanSeek { get { return true; } }
        public override bool CanWrite { get { return false; } }
        public override long Length { get { return length; } }
        public override long Position { get { return position; } set { Seek(value, SeekOrigin.Begin); } }

        public override int Read(byte[] buffer, int offset, int count)
        {
            if (position >= length || count == 0) return 0;
            int total = 0;
            while (count > 0 && position < length)
            {
                int index = files.Length - 1;
                for (int i = 0; i < files.Length; i++)
                {
                    if (position < starts[i] + files[i].Length) { index = i; break; }
                }
                FileStream file = files[index];
                long local = position - starts[index];
                file.Position = local;
                int requested = (int)Math.Min(count, file.Length - local);
                int read = file.Read(buffer, offset, requested);
                if (read <= 0) break;
                total += read;
                offset += read;
                count -= read;
                position += read;
            }
            return total;
        }

        public override long Seek(long offset, SeekOrigin origin)
        {
            long next = origin == SeekOrigin.Begin ? offset :
                (origin == SeekOrigin.Current ? position + offset : length + offset);
            if (next < 0 || next > length) throw new IOException("Seek outside setup data parts.");
            position = next;
            return position;
        }

        public override void Flush() { }
        public override void SetLength(long value) { throw new NotSupportedException(); }
        public override void Write(byte[] buffer, int offset, int count) { throw new NotSupportedException(); }

        protected override void Dispose(bool disposing)
        {
            if (disposing && files != null)
                foreach (FileStream file in files) if (file != null) file.Dispose();
            base.Dispose(disposing);
        }
    }

    private static void ReadPayloadBounds(Stream source, out long start, out long length)
    {
        if (source.Length < 16) throw new InvalidDataException("Setup payload is missing.");
        source.Position = source.Length - 16;
        byte[] footer = new byte[16];
        ReadExactly(source, footer, 0, footer.Length);
        string magic = System.Text.Encoding.ASCII.GetString(footer, 0, 8);
        if (magic != Magic) throw new InvalidDataException("Setup payload marker is invalid.");
        start = BitConverter.ToInt64(footer, 8);
        length = source.Length - 16 - start;
        if (start <= 0 || length <= 0) throw new InvalidDataException("Setup payload bounds are invalid.");
    }

    private static void Uninstall()
    {
        bool removeProfile;
        int uninstallLanguage;
        using (UninstallConfirmForm confirmation = new UninstallConfirmForm())
        {
            if (confirmation.ShowDialog() != DialogResult.Yes) return;
            removeProfile = confirmation.RemoveProfile;
            uninstallLanguage = confirmation.SelectedLanguage;
        }
        try
        {
            Registry.LocalMachine.DeleteSubKeyTree(ProductKey, false);
            string menu = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonPrograms), "ARM AI Image Enhancer");
            if (Directory.Exists(menu)) Directory.Delete(menu, true);
            string link = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonDesktopDirectory), "ARM AI Image Enhancer.lnk");
            if (File.Exists(link)) File.Delete(link);
            if (removeProfile)
            {
                string profile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "ArmAI", "ImageEnhancer");
                if (Directory.Exists(profile)) Directory.Delete(profile, true);
            }
            string root = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            ProcessStartInfo psi = new ProcessStartInfo("cmd.exe", "/c ping 127.0.0.1 -n 3 > nul & rmdir /s /q \"" + root + "\"");
            psi.CreateNoWindow = true;
            psi.UseShellExecute = false;
            Process.Start(psi);
        }
        catch (Exception ex)
        {
            MessageBox.Show(Translate("ถอนการติดตั้งไม่สำเร็จ\n\n", uninstallLanguage) + ex.Message, Translate("ARM AI Image Enhancer", uninstallLanguage), MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private sealed class UninstallConfirmForm : Form
    {
        private readonly ComboBox language;
        private readonly CheckBox removeProfile;
        internal bool RemoveProfile { get { return removeProfile.Checked; } }
        internal int SelectedLanguage { get { return Math.Max(0, language.SelectedIndex); } }

        internal UninstallConfirmForm()
        {
            Text = Translate("ถอนการติดตั้ง ARM AI Image Enhancer", 0);
            Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(470, 175);
            int selectedLanguage = GetSavedLanguageIndex();

            PictureBox languageIcon = CreateLanguageIcon(16, 12);
            language = new ComboBox { Left = 50, Top = 15, Width = 150, DropDownStyle = ComboBoxStyle.DropDownList };
            FormClosed += delegate { if (languageIcon.Image != null) languageIcon.Image.Dispose(); };
            language.Items.AddRange(new object[] { "ไทย", "English", "简体中文", "Français" });
            language.SelectedIndex = selectedLanguage;
            language.SelectedIndexChanged += delegate
            {
                ApplyTranslations(this, language.SelectedIndex);
                Text = Translate("ถอนการติดตั้ง ARM AI Image Enhancer", language.SelectedIndex);
            };

            Label prompt = new Label { Left = 18, Top = 54, Width = 430, Height = 32, Font = new Font("Tahoma", 10) };
            SetLocalized(prompt, "คุณต้องการถอนการติดตั้ง ARM AI Image Enhancer หรือไม่?", selectedLanguage);
            removeProfile = new CheckBox { Left = 18, Top = 88, Width = 430, Height = 30, Font = new Font("Tahoma", 9) };
            SetLocalized(removeProfile, "ลบการตั้งค่าและรายการล่าสุดของผู้ใช้นี้ด้วย", selectedLanguage);

            Button yes = new Button { Left = 265, Top = 128, Width = 90, Height = 30, DialogResult = DialogResult.Yes };
            SetLocalized(yes, "ถอนการติดตั้ง", selectedLanguage);
            Button no = new Button { Left = 360, Top = 128, Width = 90, Height = 30, DialogResult = DialogResult.No };
            SetLocalized(no, "ยกเลิก", selectedLanguage);
            Controls.Add(languageIcon);
            Controls.Add(language);
            Controls.Add(prompt);
            Controls.Add(removeProfile);
            Controls.Add(yes);
            Controls.Add(no);
            AcceptButton = yes;
            CancelButton = no;
        }
    }

    private static PictureBox CreateLanguageIcon(int left, int top)
    {
        PictureBox icon = new PictureBox { Left = left, Top = top, Width = 28, Height = 28,
            SizeMode = PictureBoxSizeMode.Zoom };
        using (Stream stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("lang.png"))
        {
            if (stream != null)
                using (Image image = Image.FromStream(stream)) icon.Image = new Bitmap(image);
        }
        return icon;
    }

    private static int GetSavedLanguageIndex()
    {
        try
        {
            string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "ArmAI", "ImageEnhancer", "settings.json");
            if (!File.Exists(path)) return 0;
            string settings = File.ReadAllText(path);
            if (System.Text.RegularExpressions.Regex.IsMatch(settings, "\"language\"\\s*:\\s*\"en\"", System.Text.RegularExpressions.RegexOptions.IgnoreCase)) return 1;
            if (System.Text.RegularExpressions.Regex.IsMatch(settings, "\"language\"\\s*:\\s*\"zh\"", System.Text.RegularExpressions.RegexOptions.IgnoreCase)) return 2;
            if (System.Text.RegularExpressions.Regex.IsMatch(settings, "\"language\"\\s*:\\s*\"fr\"", System.Text.RegularExpressions.RegexOptions.IgnoreCase)) return 3;
        }
        catch { }
        return 0;
    }

    private static void CreateShortcut(string linkPath, string target)
    {
        Type shellType = Type.GetTypeFromProgID("WScript.Shell");
        object shell = Activator.CreateInstance(shellType);
        object shortcut = shellType.InvokeMember("CreateShortcut", BindingFlags.InvokeMethod, null, shell, new object[] { linkPath });
        Type shortcutType = shortcut.GetType();
        shortcutType.InvokeMember("TargetPath", BindingFlags.SetProperty, null, shortcut, new object[] { target });
        shortcutType.InvokeMember("WorkingDirectory", BindingFlags.SetProperty, null, shortcut, new object[] { InstallPath });
        string iconPath = Path.Combine(InstallPath, "_internal", "ARM.ico");
        shortcutType.InvokeMember("IconLocation", BindingFlags.SetProperty, null, shortcut, new object[] { iconPath + ",0" });
        shortcutType.InvokeMember("Save", BindingFlags.InvokeMethod, null, shortcut, null);
        System.Runtime.InteropServices.Marshal.FinalReleaseComObject(shortcut);
        System.Runtime.InteropServices.Marshal.FinalReleaseComObject(shell);
    }

    private static void StartUnelevated(string applicationPath)
    {
        string explorer = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "explorer.exe");
        Process.Start(new ProcessStartInfo(explorer, "\"" + applicationPath + "\"") { UseShellExecute = true });
    }

    private static void InitializeAppLanguage(int language)
    {
        try
        {
            string profile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "ArmAI", "ImageEnhancer");
            string settings = Path.Combine(profile, "settings.json");
            if (File.Exists(settings)) return;
            string[] codes = { "th", "en", "zh", "fr" };
            Directory.CreateDirectory(profile);
            File.WriteAllText(settings, "{\"language\":\"" + codes[Math.Max(0, Math.Min(3, language))] + "\"}", new System.Text.UTF8Encoding(false));
        }
        catch { }
    }

    private sealed class InstallForm : Form
    {
        private readonly string target;
        private readonly bool register;
        private readonly long payloadBytes;
        private readonly Label message;
        private readonly Label spaceInfo;
        private readonly ProgressBar progress;
        private readonly Button installButton;
        private readonly Button cancelButton;
        private readonly Image qrImage;
        private readonly long requiredBytes;
        private readonly CheckBox desktopShortcut;
        private readonly CheckBox launchAfterInstall;
        private readonly Label title;
        private readonly ComboBox languageSelector;
        private readonly PictureBox languageIcon;
        private int LanguageIndex { get { return languageSelector == null ? 0 : Math.Max(0, languageSelector.SelectedIndex); } }
        private int activeInstallLanguage;
        private volatile bool cancelRequested;
        private volatile bool installationRunning;
        private volatile bool commitStarted;
        private bool allowClose;
        private readonly Label qrMood;
        private readonly Label qrSmile;

        internal InstallForm(string targetPath, bool writeRegistration, long payloadSize, Image qr)
        {
            target = targetPath;
            register = writeRegistration;
            payloadBytes = payloadSize;
            qrImage = qr;
            requiredBytes = payloadBytes + ReserveBytes;
            Text = "ARM AI Image Enhancer — Setup";
            Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            ClientSize = new Size(790, 570);
            AutoScroll = true;

            PictureBox brandIcon = new PictureBox { Left = 22, Top = 16, Width = 36, Height = 36,
                SizeMode = PictureBoxSizeMode.Zoom, Image = Icon.ExtractAssociatedIcon(Application.ExecutablePath).ToBitmap() };
            Controls.Add(brandIcon);
            title = new Label { Left = 66, Top = 16, Width = 465, Height = 36,
                Font = new Font("Tahoma", 16, FontStyle.Bold), TextAlign = ContentAlignment.MiddleLeft };
            SetLocalized(title, "ติดตั้ง ARM AI Image Enhancer V.", 0);
            Controls.Add(title);
            languageIcon = CreateLanguageIcon(568, 15);
languageSelector = new ComboBox { Left = 602, Top = 15, Width = 168, Height = 28, DropDownStyle = ComboBoxStyle.DropDownList };
            languageSelector.Items.AddRange(new object[] { "ไทย", "English", "简体中文", "Français" });
            languageSelector.SelectedIndex = 0;
            languageSelector.SelectedIndexChanged += delegate { ApplyLanguage(); };
            Controls.Add(languageIcon);
            Controls.Add(languageSelector);
            Label intro = new Label { Left = 22, Top = 56, Width = 510, Height = 42, Font = new Font("Tahoma", 10), AutoSize = false };
            SetLocalized(intro, "โปรดตรวจสอบพื้นที่และรายละเอียดก่อนเริ่มติดตั้ง โปรแกรมจะติดตั้งลงใน C:\\Program Files\\ArmAI\\ImageEnhancer", 0);
            Controls.Add(intro);

            Label specs = new Label { Left = 22, Top = 106, Width = 510, Height = 178, Font = new Font("Tahoma", 10), AutoSize = false };
            SetLocalized(specs, "ข้อมูลสำคัญ", 0);
            Controls.Add(specs);

            long available = new DriveInfo("C:\\").AvailableFreeSpace;
            double installGb = payloadBytes / 1000000000.0;
            double requiredGb = requiredBytes / 1000000000.0;
            double setupGb = new FileInfo(Application.ExecutablePath).Length / 1000000000.0;
            spaceInfo = new Label { Left = 22, Top = 290, Width = 510, Height = 84,
                Text = String.Format("พื้นที่ว่าง C: {0:N1} GB\nต้องเหลืออย่างน้อย {1:N1} GB เพื่อติดตั้งไฟล์โปรแกรมประมาณ {2:N1} GB พร้อมพื้นที่สำรอง 1 GB\nหากไฟล์ Setup อยู่บน C: ควรเตรียมพื้นที่ประมาณ {3:N1} GB ก่อนดาวน์โหลด (รวมไฟล์ติดตั้งราว {4:N1} GB)",
                    available / 1000000000.0, requiredGb, installGb, requiredGb + setupGb, setupGb),
                Font = new Font("Tahoma", 10, FontStyle.Bold), AutoSize = false, ForeColor = available >= requiredBytes ? Color.DarkGreen : Color.DarkRed };
            spaceInfo.Tag = "พื้นที่ว่าง C: {0:N1} GB\nต้องเหลืออย่างน้อย {1:N1} GB เพื่อติดตั้งไฟล์โปรแกรมประมาณ {2:N1} GB พร้อมพื้นที่สำรอง 1 GB\nหากไฟล์ Setup อยู่บน C: ควรเตรียมพื้นที่ประมาณ {3:N1} GB ก่อนดาวน์โหลด (รวมไฟล์ติดตั้งราว {4:N1} GB)";
            Controls.Add(spaceInfo);

            Label qrTitle = new Label { Left = 550, Top = 56, Width = 220, Height = 48,
                Font = new Font("Tahoma", 10, FontStyle.Bold), TextAlign = ContentAlignment.MiddleCenter };
            SetLocalized(qrTitle, "ช่วยสนับสนุนการพัฒนาโปรแกรม\n5 บาท 10 บาท ได้หมดครับ", 0);
            Controls.Add(qrTitle);
            qrMood = new Label { Left = 550, Top = 103, Width = 220, Height = 22,
                Font = new Font("Tahoma", 10, FontStyle.Bold), TextAlign = ContentAlignment.MiddleCenter };
            SetLocalized(qrMood, "แล้วแต่ศรัทธา", 0);
            Controls.Add(qrMood);
            qrSmile = new Label { Left = 0, Top = 104, Width = 18, Height = 20,
                Text = "\U0001F606", Font = new Font("Segoe UI Emoji", 8, FontStyle.Regular),
                TextAlign = ContentAlignment.MiddleLeft };
            Controls.Add(qrSmile);
            PictureBox picture = new PictureBox { Left = 575, Top = 138, Width = 170, Height = 280,
                SizeMode = PictureBoxSizeMode.Zoom, BorderStyle = BorderStyle.FixedSingle, Image = qrImage };
            Controls.Add(picture);
            Label scan = new Label { Left = 550, Top = 420, Width = 220, Height = 28,
                Font = new Font("Tahoma", 9), TextAlign = ContentAlignment.MiddleCenter };
            SetLocalized(scan, "สแกน QR PromptPay เพื่อสนับสนุน", 0);
            Controls.Add(scan);

            message = new Label { Left = 22, Top = 391, Width = 510, Height = 28, Text = "",
                Font = new Font("Tahoma", 10), AutoEllipsis = true };
            progress = new ProgressBar { Left = 22, Top = 420, Width = 510, Height = 20, Minimum = 0, Maximum = 100, Style = ProgressBarStyle.Continuous, Visible = false };
            Controls.Add(message);
            Controls.Add(progress);

            desktopShortcut = new CheckBox { Left = 22, Top = 490, Width = 360, Height = 25, Checked = true,
                Font = new Font("Tahoma", 9), Visible = writeRegistration };
            SetLocalized(desktopShortcut, "สร้างไอคอน ARM AI Image Enhancer บน Desktop", 0);
            Controls.Add(desktopShortcut);
            launchAfterInstall = new CheckBox { Left = 22, Top = 517, Width = 360, Height = 25, Checked = true,
                Font = new Font("Tahoma", 9), Visible = writeRegistration };
            SetLocalized(launchAfterInstall, "เปิดโปรแกรมหลังติดตั้งเสร็จ", 0);
            Controls.Add(launchAfterInstall);
            installButton = new Button { Left = 402, Top = 520, Width = 145, Height = 34, Font = new Font("Tahoma", 10, FontStyle.Bold), Enabled = available >= requiredBytes };
            SetLocalized(installButton, "ติดตั้ง", 0);
            installButton.Click += delegate { BeginInstallation(); };
            cancelButton = new Button { Left = 562, Top = 520, Width = 145, Height = 34, Font = new Font("Tahoma", 10) };
            SetLocalized(cancelButton, "ยกเลิก", 0);
            cancelButton.Click += delegate { RequestCancel(); };
            Controls.Add(installButton);
            Controls.Add(cancelButton);
            FormClosed += delegate
            {
                if (qrImage != null) qrImage.Dispose();
                if (brandIcon.Image != null) brandIcon.Image.Dispose();
                if (languageIcon.Image != null) languageIcon.Image.Dispose();
            };
            FormClosing += delegate(object sender, FormClosingEventArgs e)
            {
                if (installationRunning && !allowClose)
                {
                    e.Cancel = true;
                    RequestCancel();
                }
            };
            ApplyLanguage();
        }

        private void ApplyLanguage()
        {
            int language = LanguageIndex;
            ApplyTranslations(this, language);
            title.Text = Translate("ติดตั้ง ARM AI Image Enhancer V.", language) + AppVersion;
            double available = new DriveInfo("C:\\").AvailableFreeSpace / 1000000000.0;
            double installGb = payloadBytes / 1000000000.0;
            double requiredGb = requiredBytes / 1000000000.0;
            double setupGb = new FileInfo(Application.ExecutablePath).Length / 1000000000.0;
            string key = spaceInfo.Tag as string;
            spaceInfo.Text = String.Format(Translate(key, language), available, requiredGb, installGb, requiredGb + setupGb, setupGb);
            LayoutSpaceDetails();
            SizeF moodSize;
            using (Graphics graphics = CreateGraphics()) moodSize = graphics.MeasureString(qrMood.Text, qrMood.Font);
            int moodWidth = Math.Min(220, (int)Math.Ceiling(moodSize.Width));
            qrMood.Left = 550 + (220 - moodWidth) / 2;
            qrMood.Width = moodWidth;
            qrSmile.Left = Math.Min(766, qrMood.Left + moodWidth + 1);
        }

        private void LayoutSpaceDetails()
        {
            // Measure wrapped text using the label renderer for each language and DPI.
            int height = Math.Max(84, spaceInfo.GetPreferredSize(new Size(spaceInfo.Width, 0)).Height + 8);
            int extra = height - 84;
            spaceInfo.Height = height;
            message.Top = 391 + extra;
            progress.Top = 420 + extra;
            desktopShortcut.Top = 490 + extra;
            launchAfterInstall.Top = 517 + extra;
            installButton.Top = cancelButton.Top = 520 + extra;
            ClientSize = new Size(790, 570 + extra);
            AutoScrollMinSize = new Size(790, 570 + extra);
        }

        private void RequestCancel()
        {
            if (!installationRunning)
            {
                allowClose = true;
                Close();
                return;
            }
            if (commitStarted) return;
            DialogResult answer = MessageBox.Show(this,
                Translate("ยืนยันยกเลิกการติดตั้งหรือไม่? ไฟล์ชั่วคราวจะถูกลบออก", activeInstallLanguage),
                Translate("ยกเลิกการติดตั้ง", activeInstallLanguage), MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (answer != DialogResult.Yes) return;
            cancelRequested = true;
            cancelButton.Enabled = false;
            message.Text = Translate("กำลังยกเลิกและลบไฟล์ชั่วคราว…", activeInstallLanguage);
        }

        private void ThrowIfCancellationRequested()
        {
            if (cancelRequested && !commitStarted) throw new OperationCanceledException();
        }

        private void BeginInstallation()
        {
            long available = new DriveInfo("C:\\").AvailableFreeSpace;
            if (available < requiredBytes)
            {
                MessageBox.Show(this, String.Format(Translate("พื้นที่ C: ไม่เพียงพอ\nต้องการอย่างน้อย {0:N1} GB แต่เหลือ {1:N1} GB\nลบไฟล์ที่ไม่ใช้งานหรือเลือกติดตั้งภายหลังเมื่อเพิ่มพื้นที่แล้ว", LanguageIndex),
                    requiredBytes / 1000000000.0, available / 1000000000.0), Translate("พื้นที่ไม่เพียงพอ", LanguageIndex), MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            activeInstallLanguage = LanguageIndex;
            languageSelector.Enabled = false;
            installButton.Enabled = false;
            cancelButton.Enabled = true;
            installationRunning = true;
            message.Text = Translate("กำลังเตรียมติดตั้ง…", activeInstallLanguage);
            progress.Visible = true;
            System.Threading.ThreadPool.QueueUserWorkItem(delegate { Install(); });
        }

        private void SetProgress(string text, int value)
        {
            if (IsDisposed) return;
            BeginInvoke((Action)delegate { message.Text = text; progress.Value = Math.Max(0, Math.Min(100, value)); });
        }

        private void Install()
        {
            // A sibling inherits install-parent permissions and stays on the target volume.
            string stage = target + ".__staging_" + Guid.NewGuid().ToString("N");
            string backup = target + ".__previous_" + Guid.NewGuid().ToString("N");
            bool oldMoved = false;
            bool newMoved = false;
            bool committed = false;
            RegistrationSnapshot registration = null;
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(target));
                Directory.CreateDirectory(stage);
                ThrowIfCancellationRequested();
                using (PayloadStream payload = new PayloadStream(Assembly.GetExecutingAssembly().Location))
                using (ZipArchive archive = new ZipArchive(payload.Content, ZipArchiveMode.Read, true))
                {
                    long total = 0;
                    foreach (ZipArchiveEntry entry in archive.Entries) total += entry.Length;
                    long done = 0;
                    int shown = -1;
                    byte[] buffer = new byte[1024 * 1024];
                    foreach (ZipArchiveEntry entry in archive.Entries)
                    {
                        ThrowIfCancellationRequested();
                        string dest = Path.GetFullPath(Path.Combine(stage, entry.FullName.Replace('/', Path.DirectorySeparatorChar)));
                        string prefix = Path.GetFullPath(stage).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
                        if (!dest.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Unsafe setup path: " + entry.FullName);
                        if (entry.FullName.EndsWith("/", StringComparison.Ordinal)) { Directory.CreateDirectory(dest); continue; }
                        Directory.CreateDirectory(Path.GetDirectoryName(dest));
                        using (Stream input = entry.Open())
                        using (FileStream output = new FileStream(dest, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                        {
                            int count;
                            while ((count = input.Read(buffer, 0, buffer.Length)) > 0)
                            {
                                ThrowIfCancellationRequested();
                                output.Write(buffer, 0, count);
                                done += count;
                                int percent = total == 0 ? 100 : (int)(done * 100 / total);
                                if (percent != shown) { shown = percent; SetProgress(String.Format(Translate("กำลังติดตั้งไฟล์โปรแกรม… {0}%", activeInstallLanguage), percent), percent); }
                            }
                        }
                    }
                }

                SetProgress(Translate("กำลังย้ายไฟล์จากโฟลเดอร์ชั่วคราว…", activeInstallLanguage), 99);
                ThrowIfCancellationRequested();
                if (Directory.Exists(target)) { RetryFileOperation(delegate { Directory.Move(target, backup); }); oldMoved = true; }
                ThrowIfCancellationRequested();
                try
                {
                    RetryFileOperation(delegate { Directory.Move(stage, target); });
                }
                catch (IOException)
                {
                    CopyStagedInstallation(stage, ref newMoved);
                }
                catch (UnauthorizedAccessException)
                {
                    CopyStagedInstallation(stage, ref newMoved);
                }
                newMoved = true;
                ThrowIfCancellationRequested();
                if (register)
                {
                    registration = CaptureRegistration();
                    RegisterInstall(desktopShortcut.Checked);
                    InitializeAppLanguage(activeInstallLanguage);
                }
                ThrowIfCancellationRequested();
                commitStarted = true;
                committed = true;
                if (Directory.Exists(stage)) DeleteTree(stage);
                if (oldMoved && Directory.Exists(backup)) DeleteTree(backup);
                SetProgress(Translate("ติดตั้งเสร็จแล้ว", activeInstallLanguage), 100);
                BeginInvoke((Action)delegate
                {
                    installationRunning = false;
                    allowClose = true;
                    bool launch = register && launchAfterInstall.Checked;
                    MessageBox.Show(this, Translate("ติดตั้ง ARM AI Image Enhancer เรียบร้อยแล้วที่:\n", LanguageIndex) + target,
                        Translate("ติดตั้งสำเร็จ", LanguageIndex), MessageBoxButtons.OK, MessageBoxIcon.Information);
                    Close();
                    if (launch) StartUnelevated(Path.Combine(target, "ArmAIImageEnhancer.exe"));
                });
            }
            catch (OperationCanceledException)
            {
                string cleanupNote = "";
                if (!committed && newMoved && Directory.Exists(target))
                {
                    try { DeleteTree(target); } catch (Exception cleanupError) { cleanupNote += "\nลบโฟลเดอร์ใหม่ไม่สำเร็จ: " + cleanupError.Message; }
                }
                if (!committed && oldMoved && Directory.Exists(backup) && !Directory.Exists(target))
                {
                    try { RetryFileOperation(delegate { Directory.Move(backup, target); }); } catch (Exception cleanupError) { cleanupNote += "\nกู้คืนโฟลเดอร์เดิมไม่สำเร็จ: " + cleanupError.Message; }
                }
                if (Directory.Exists(stage))
                {
                    try { DeleteTree(stage); } catch (Exception cleanupError) { cleanupNote += "\nลบไฟล์ชั่วคราวไม่สำเร็จ: " + cleanupError.Message; }
                }
                if (!committed && registration != null)
                {
                    try { RestoreRegistration(registration); } catch (Exception cleanupError) { cleanupNote += "\nคืนค่าข้อมูลเดิมไม่สำเร็จ: " + cleanupError.Message; }
                }
                BeginInvoke((Action)delegate
                {
                    installationRunning = false;
                    allowClose = true;
                    if (cleanupNote.Length == 0)
                        MessageBox.Show(this, Translate("การติดตั้งถูกยกเลิกและลบไฟล์ชั่วคราวแล้ว", activeInstallLanguage),
                            Translate("ยกเลิกการติดตั้ง", activeInstallLanguage), MessageBoxButtons.OK, MessageBoxIcon.Information);
                    else
                        MessageBox.Show(this, Translate("การติดตั้งถูกยกเลิกและลบไฟล์ชั่วคราวแล้ว", activeInstallLanguage) + cleanupNote,
                            Translate("ยกเลิกการติดตั้ง", activeInstallLanguage), MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    Close();
                });
            }
            catch (Exception ex)
            {
                string cleanupNote = "";
                if (!committed && newMoved && Directory.Exists(target))
                {
                    try { DeleteTree(target); } catch (Exception cleanupError) { cleanupNote += "\nลบโฟลเดอร์ใหม่ไม่สำเร็จ: " + cleanupError.Message; }
                }
                if (!committed && oldMoved && Directory.Exists(backup) && !Directory.Exists(target))
                {
                    try { RetryFileOperation(delegate { Directory.Move(backup, target); }); } catch (Exception cleanupError) { cleanupNote += "\nกู้คืนโฟลเดอร์เดิมไม่สำเร็จ: " + cleanupError.Message; }
                }
                if (Directory.Exists(stage))
                {
                    try { DeleteTree(stage); } catch (Exception cleanupError) { cleanupNote += "\nลบไฟล์ชั่วคราวไม่สำเร็จ: " + cleanupError.Message; }
                }
                if (!committed && registration != null)
                {
                    try { RestoreRegistration(registration); } catch (Exception cleanupError) { cleanupNote += "\nคืนค่าทางลัดหรือข้อมูลถอนการติดตั้งไม่สำเร็จ: " + cleanupError.Message; }
                }
                string error = committed
                    ? "เวอร์ชันใหม่ติดตั้งแล้ว แต่ลบไฟล์ชั่วคราวหรือไฟล์เวอร์ชันเดิมไม่สำเร็จ: " + ex.Message + cleanupNote
                    : Translate("ติดตั้งไม่สำเร็จ ระบบลบไฟล์ชั่วคราวและพยายามคืนไฟล์เดิมแล้ว\n\n", activeInstallLanguage) + ex.Message + cleanupNote;
                BeginInvoke((Action)delegate
                {
                    installationRunning = false;
                    allowClose = true;
                    MessageBox.Show(this, error,
                        Translate("ติดตั้งไม่สำเร็จ", activeInstallLanguage), MessageBoxButtons.OK, MessageBoxIcon.Error);
                    Close();
                });
            }
        }

        private void CopyStagedInstallation(string stage, ref bool newMoved)
        {
            // The fallback needs extra space while the staged payload remains on disk.
            long available = new DriveInfo(Path.GetPathRoot(target)).AvailableFreeSpace;
            if (available < requiredBytes)
                throw new IOException("Not enough free space for the installation copy fallback.");
            // Mark first so rollback removes even a partially copied installation.
            newMoved = true;
            CopyDirectory(stage, target);
            ThrowIfCancellationRequested();
        }

        private static void RetryFileOperation(Action operation)
        {
            for (int attempt = 0; ; attempt++)
            {
                try { operation(); return; }
                catch (IOException) { if (attempt >= 3) throw; }
                catch (UnauthorizedAccessException) { if (attempt >= 3) throw; }
                System.Threading.Thread.Sleep(250 * (attempt + 1));
            }
        }

        private void CopyDirectory(string source, string destination)
        {
            Directory.CreateDirectory(destination);
            foreach (string directory in Directory.GetDirectories(source, "*", SearchOption.AllDirectories))
                Directory.CreateDirectory(Path.Combine(destination, directory.Substring(source.TrimEnd(Path.DirectorySeparatorChar).Length + 1)));
            string[] files = Directory.GetFiles(source, "*", SearchOption.AllDirectories);
            long total = 0;
            foreach (string file in files) total += new FileInfo(file).Length;
            long done = 0;
            int shown = -1;
            byte[] buffer = new byte[1024 * 1024];
            foreach (string file in files)
            {
                string relative = file.Substring(source.TrimEnd(Path.DirectorySeparatorChar).Length + 1);
                string outputPath = Path.Combine(destination, relative);
                Directory.CreateDirectory(Path.GetDirectoryName(outputPath));
                using (FileStream input = new FileStream(file, FileMode.Open, FileAccess.Read, FileShare.Read))
                using (FileStream output = new FileStream(outputPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    int count;
                    while ((count = input.Read(buffer, 0, buffer.Length)) > 0)
                    {
                        ThrowIfCancellationRequested();
                        output.Write(buffer, 0, count);
                        done += count;
                        int percent = total == 0 ? 100 : 96 + (int)(done * 3 / total);
                        if (percent != shown)
                        {
                            shown = percent;
                            SetProgress(String.Format(Translate("กำลังคัดลอกไฟล์เข้าตำแหน่งติดตั้ง… {0}%", activeInstallLanguage), percent), percent);
                        }
                    }
                }
            }
        }

        private void RegisterInstall(bool createDesktopShortcut)
        {
            string app = Path.Combine(target, "ArmAIImageEnhancer.exe");
            string uninstaller = Path.Combine(target, "Uninstall.exe");
            if (!File.Exists(uninstaller)) throw new FileNotFoundException("Uninstaller payload is missing.", uninstaller);
            string menu = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonPrograms), "ARM AI Image Enhancer");
            Directory.CreateDirectory(menu);
            CreateShortcut(Path.Combine(menu, "ARM AI Image Enhancer.lnk"), app);
            string desktopLink = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonDesktopDirectory), "ARM AI Image Enhancer.lnk");
            if (createDesktopShortcut) CreateShortcut(desktopLink, app);
            else if (File.Exists(desktopLink)) File.Delete(desktopLink);
            using (RegistryKey key = Registry.LocalMachine.CreateSubKey(ProductKey))
            {
                key.SetValue("DisplayName", "ARM AI Image Enhancer");
                key.SetValue("DisplayVersion", AppVersion);
                key.SetValue("Publisher", "ARM AI");
                key.SetValue("InstallLocation", target);
                key.SetValue("UninstallString", "\"" + uninstaller + "\" --uninstall");
                key.SetValue("DisplayIcon", app);
                key.SetValue("NoModify", 1, RegistryValueKind.DWord);
                key.SetValue("NoRepair", 1, RegistryValueKind.DWord);
            }
        }

        private static RegistrationSnapshot CaptureRegistration()
        {
            RegistrationSnapshot snapshot = new RegistrationSnapshot();
            using (RegistryKey key = Registry.LocalMachine.OpenSubKey(ProductKey, false))
            {
                if (key != null)
                {
                    snapshot.KeyExists = true;
                    foreach (string name in key.GetValueNames())
                    {
                        snapshot.Values[name] = key.GetValue(name, null, RegistryValueOptions.DoNotExpandEnvironmentNames);
                        snapshot.Kinds[name] = key.GetValueKind(name);
                    }
                }
            }
            snapshot.MenuDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonPrograms), "ARM AI Image Enhancer");
            snapshot.MenuDirectoryExisted = Directory.Exists(snapshot.MenuDirectory);
            snapshot.MenuShortcutPath = Path.Combine(snapshot.MenuDirectory, "ARM AI Image Enhancer.lnk");
            snapshot.DesktopShortcutPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonDesktopDirectory), "ARM AI Image Enhancer.lnk");
            snapshot.MenuShortcutExisted = File.Exists(snapshot.MenuShortcutPath);
            snapshot.DesktopShortcutExisted = File.Exists(snapshot.DesktopShortcutPath);
            if (snapshot.MenuShortcutExisted) snapshot.MenuShortcut = File.ReadAllBytes(snapshot.MenuShortcutPath);
            if (snapshot.DesktopShortcutExisted) snapshot.DesktopShortcut = File.ReadAllBytes(snapshot.DesktopShortcutPath);
            return snapshot;
        }

        private static void RestoreRegistration(RegistrationSnapshot snapshot)
        {
            if (snapshot.KeyExists)
            {
                using (RegistryKey key = Registry.LocalMachine.CreateSubKey(ProductKey))
                {
                    foreach (string name in key.GetValueNames()) key.DeleteValue(name, false);
                    foreach (KeyValuePair<string, object> entry in snapshot.Values)
                        key.SetValue(entry.Key, entry.Value, snapshot.Kinds[entry.Key]);
                }
            }
            else Registry.LocalMachine.DeleteSubKeyTree(ProductKey, false);

            RestoreFile(snapshot.MenuShortcutPath, snapshot.MenuShortcutExisted, snapshot.MenuShortcut);
            RestoreFile(snapshot.DesktopShortcutPath, snapshot.DesktopShortcutExisted, snapshot.DesktopShortcut);
            if (!snapshot.MenuDirectoryExisted && Directory.Exists(snapshot.MenuDirectory) && Directory.GetFileSystemEntries(snapshot.MenuDirectory).Length == 0)
                Directory.Delete(snapshot.MenuDirectory);
        }

        private static void RestoreFile(string path, bool existed, byte[] contents)
        {
            if (existed)
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllBytes(path, contents);
            }
            else if (File.Exists(path)) File.Delete(path);
        }

        private static void DeleteTree(string path)
        {
            if (!Directory.Exists(path)) return;
            foreach (string file in Directory.GetFiles(path, "*", SearchOption.AllDirectories))
            {
                try { File.SetAttributes(file, FileAttributes.Normal); } catch { }
            }
            foreach (string directory in Directory.GetDirectories(path, "*", SearchOption.AllDirectories))
                File.SetAttributes(directory, FileAttributes.Normal);
            File.SetAttributes(path, FileAttributes.Normal);
            RetryFileOperation(delegate { Directory.Delete(path, true); });
        }
    }

    private static void ReadExactly(Stream stream, byte[] buffer, int offset, int count)
    {
        while (count > 0)
        {
            int read = stream.Read(buffer, offset, count);
            if (read <= 0) throw new EndOfStreamException();
            offset += read;
            count -= read;
        }
    }

    private sealed class SegmentStream : Stream
    {
        private readonly Stream source;
        private readonly long start;
        private readonly long length;
        private long position;
        internal SegmentStream(Stream sourceStream, long offset, long size) { source = sourceStream; start = offset; length = size; source.Position = offset; }
        public override bool CanRead { get { return source.CanRead; } }
        public override bool CanSeek { get { return source.CanSeek; } }
        public override bool CanWrite { get { return false; } }
        public override long Length { get { return length; } }
        public override long Position { get { return position; } set { Seek(value, SeekOrigin.Begin); } }
        public override int Read(byte[] buffer, int offset, int count)
        {
            if (position >= length) return 0;
            int n = source.Read(buffer, offset, (int)Math.Min(count, length - position));
            position += n;
            return n;
        }
        public override long Seek(long offset, SeekOrigin origin)
        {
            long next = origin == SeekOrigin.Begin ? offset : (origin == SeekOrigin.Current ? position + offset : length + offset);
            if (next < 0 || next > length) throw new IOException("Seek outside setup payload.");
            position = next;
            source.Position = start + position;
            return position;
        }
        public override void Flush() { }
        public override void SetLength(long value) { throw new NotSupportedException(); }
        public override void Write(byte[] buffer, int offset, int count) { throw new NotSupportedException(); }
    }
}
