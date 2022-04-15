import torch
from torchvision.transforms.functional import to_tensor, to_pil_image
from PIL import Image

model = torch.jit.load('./models/torchscript_resnet50_fp32.pth').cuda().eval()

bgr= Image.open('./images/input/bkg_img.jpg')
src= Image.open('./images/input/main_img.jpg')

src = to_tensor(src).cuda().unsqueeze(0)
bgr = to_tensor(bgr).cuda().unsqueeze(0)

if src.size(2) <= 2048 and src.size(3) <= 2048:
  model.backbone_scale = 1/4
  model.refine_sample_pixels = 80_000
else:
  model.backbone_scale = 1/8
  model.refine_sample_pixels = 320_000

pha, fgr = model(src, bgr)[:2]

com = pha * fgr + (1 - pha) * torch.tensor([120/255, 255/255, 155/255], device='cuda').view(1, 3, 1, 1)

to_pil_image(com[0].cpu()).save('./images/output/result.png')
to_pil_image(pha[0].cpu()).save('./images/output/pha.png')
to_pil_image(fgr[0].cpu()).save('./images/output/fgr.png')