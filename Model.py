import torch
import torch.nn as nn

class CustomUNet(nn.Module):
    def __init__(self):
        super().__init__()

        def block_conv(in_feat, out_feat):
            return nn.Sequential(
                nn.Conv2d(in_feat, out_feat, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_feat),
                nn.ReLU(inplace=True)
            )

        self.encoder_layer1 = nn.Sequential(block_conv(3, 64), block_conv(64, 64))
        self.encoder_pool1 = nn.MaxPool2d(2)
        self.encoder_layer2 = nn.Sequential(block_conv(64, 128), block_conv(128, 128))
        self.encoder_pool2 = nn.MaxPool2d(2)

        self.bridge = nn.Sequential(block_conv(128, 256), block_conv(256, 256))

        self.upconv_layer1 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.decoder_layer1 = nn.Sequential(block_conv(256, 128), block_conv(128, 64))
        self.upconv_layer2 = nn.ConvTranspose2d(64, 64, kernel_size=2, stride=2)
        self.decoder_layer2 = nn.Sequential(block_conv(128, 64), block_conv(64, 32))

        self.output_layer = nn.Conv2d(32, 1, kernel_size=1)

    def forward(self, input_tensor):
        enc1 = self.encoder_layer1(input_tensor)
        enc2 = self.encoder_layer2(self.encoder_pool1(enc1))
        bridge_out = self.bridge(self.encoder_pool2(enc2))
        up1 = self.upconv_layer1(bridge_out)
        dec1 = self.decoder_layer1(torch.cat([up1, enc2], dim=1))
        up2 = self.upconv_layer2(dec1)
        dec2 = self.decoder_layer2(torch.cat([up2, enc1], dim=1))
        output = torch.sigmoid(self.output_layer(dec2))
        return output
