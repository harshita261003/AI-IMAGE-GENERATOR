import tkinter
import customtkinter as ctk
from PIL import ImageTk
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("dark-blue")  


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
      
        self.default_window_width = 1200
        self.default_window_height = 800
        self.authorization_token = "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"

        self.title("Image Generator")
        self.geometry(f"{self.default_window_width}x{self.default_window_height}")


        self.windowlabel = ctk.CTkLabel(self, text="AI Image Generator",
                                        font=ctk.CTkFont(size=30, weight="bold"), padx=50, pady=50, text_color="white")
        self.windowlabel.pack()
        self.promptlabel = ctk.CTkLabel(self, text="Prompt",
                                        font=ctk.CTkFont(family="Times New Roman", size=20, weight="bold"),
                                        text_color="white")
        self.promptlabel.pack()
        self.promptentry = ctk.CTkEntry(self, placeholder_text="Enter your prompt here",
                                        width=self.default_window_width - 20, height=40)
        self.promptentry.pack(padx=20, pady=20)

        self.generatebutton = ctk.CTkButton(master=self, text="Generate Image", width=self.default_window_width - 50,
                                            height=40, fg_color="transparent", border_width=2, text_color="white",
                                            command=self.generate)
        self.generatebutton.pack()

        self.clearbutton = ctk.CTkButton(master=self, text="Clear Image", width=self.default_window_width - 50,
                                         height=40, fg_color="transparent", border_width=2, text_color="white",
                                         command=self.clear)
        self.clearbutton.pack(pady=20)

        self.imageview = None  # Keep track of the image label

    def generate(self):
        self.textprompt = self.promptentry.get()

        self.generatebutton.configure(state="disabled")

        self.progress = ctk.CTkProgressBar(master=self, orientation='horizontal', mode='indeterminate')
        self.progress.pack()
        self.progress.start()

        self.modelid = "CompVis/stable-diffusion-v1-4"
        self.device = torch.device("cuda")
        self.pipe = StableDiffusionPipeline.from_pretrained(self.modelid, revision="fp16", torch_dtype=torch.float16,
                                                            use_auth_token=self.authorization_token)
        self.pipe.to(self.device)

        with autocast(device_type=self.device.type):  # Pass the device type here
            self.image = self.pipe(self.textprompt, guidance_scale=8.5).images[0]
            self.image.save('generatedimage.png')
            self.img = ImageTk.PhotoImage(self.image)

           
            if self.imageview:
                self.imageview.pack_forget()

       
            self.imageview = ctk.CTkLabel(self, width=600, height=400)
            self.imageview.pack()
            self.imageview.configure(image=self.img)

        self.progress.stop()
        self.progress.pack_forget()
        self.generatebutton.configure(state="normal")

    def clear(self):
      
        if self.imageview:
            self.imageview.pack_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
