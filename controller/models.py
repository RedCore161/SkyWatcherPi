from django.db import models


APERTURES = [('4', '4'), ('4.5', '4.5'), ('5', '5'), ('5.6', '5.6'), ('6.3', '6.3'), ('7.1', '7.1'), ('8', '8'),
             ('9', '9'), ('10', '10'), ('11', '11'), ('13', '13'), ('14', '14'), ('16', '16'), ('18', '18'),
             ('20', '20'), ('22', '22')]

EXPOSURES = [('30', '30'), ('25', '25'), ('20', '20'), ('15', '15'), ('13', '13'), ('10', '10'), ('8', '8'), ('6', '6'),
             ('5', '5'), ('4', '4'), ('3.2', '3.2'), ('2.5', '2.5'), ('2', '2'), ('1.6', '1.6'), ('1.3', '1.3'),
             ('1', '1'), ('0.8', '0.8'), ('0.6', '0.6'), ('0.5', '0.5'), ('0.4', '0.4'), ('0.3', '0.3'), ('1/4', '1/4'),
             ('1/5', '1/5'), ('1/6', '1/6'), ('1/8', '1/8'), ('1/10', '1/10'), ('1/13', '1/13'), ('1/15', '1/15'),
             ('1/20', '1/20'), ('1/25', '1/25'), ('1/30', '1/30'), ('1/40', '1/40'), ('1/50', '1/50'), ('1/60', '1/60'),
             ('1/80', '1/80'), ('1/100', '1/100'), ('1/4000', '1/4000')]

ISOS = [('100', '100'), ('200', '200'), ('400', '400'), ('800', '800'), ('1600', '1600'), ('3200', '3200'),
        ('6400', '6400'), ('12800', '12800'), ('25600', '25600')]

FORMAT_TYPES = [('Large Fine JPEG', 'Large Fine JPEG'), ('Large Normal JPEG', 'Large Normal JPEG'),
                ('Medium Fine JPEG', 'Medium Fine JPEG'), ('Medium Normal JPEG', 'Medium Normal JPEG'),
                ('Small Fine JPEG', 'Small Fine JPEG'), ('Small Normal JPEG', 'Small Normal JPEG'),
                ('Small JPEG', 'Small JPEG'), ('RAW + Large Fine JPEG ', 'RAW + Large Fine JPEG'), ('RAW  ', 'RAW')]

IMAGE_TYPES = [('0', 'Preview'), ('1', 'Focus'), ('2', 'Full')]

# Add Model-Ids to the name?
SHOW_IDS = True


class CaptureFlow(models.Model):
    """
    container to bundle a set of CaptureConfigs
    """
    name = models.CharField(max_length=300, null=True)

    def __str__(self):
        if SHOW_IDS:
            return "[{}] {}".format(self.pk, self.name)
        return self.name


class CaptureConfig(models.Model):
    """
    holds most of a data to capture an image
    """
    description = models.CharField(max_length=300, null=True)

    bulb_time = models.IntegerField(default=0)
    exposure = models.CharField(max_length=6, null=True, choices=EXPOSURES, default=EXPOSURES[19][0])
    aperture = models.CharField(max_length=3, null=False, choices=APERTURES, default=APERTURES[9][0])
    iso = models.CharField(max_length=5, null=False, choices=ISOS)
    image_format = models.CharField(max_length=25, null=False, choices=FORMAT_TYPES)

    def __str__(self):
        _id = ''
        if SHOW_IDS:
            _id = "[{}] ".format(self.pk)

        if self.bulb_time != 0:
            return "{}{}(blub: {}s/ {} / iso: {})".format(_id, self.description, self.bulb_time, self.aperture, self.iso)
        return "{}{}({}s/ {} / iso: {} )".format(_id, self.description, self.exposure, self.aperture, self.iso)


class ConfigMapping(models.Model):
    """
    mapping table for Many-2-Many-relation between CaptureFlow and CaptureConfig
    also saves how many iterations should be performed, and in which order it will be displayed
    see https://docs.djangoproject.com/en/3.0/topics/db/examples/many_to_many/
    """
    flow = models.ForeignKey(CaptureFlow, on_delete=models.CASCADE)
    config = models.ForeignKey(CaptureConfig, on_delete=models.CASCADE)
    repeats = models.IntegerField(default=1)
    order = models.IntegerField(default=1)

    def __str__(self):
        if SHOW_IDS:
            return "[{}] Map flow[{}] => config[{}]".format(self.pk, self.flow.id, self.config.id)
        return "Map flow[{}] => config[{}]".format(self.flow.id, self.config.id)


class ImageFile(models.Model):
    """
    basic image model - whenever a image is captured this on is created
    """
    filename = models.CharField(max_length=200, null=True)
    path = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    config = models.ForeignKey(CaptureConfig, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, null=True, choices=IMAGE_TYPES)
    description = models.CharField(max_length=200, null=True)

    def create_as_preview(self, filename):
        self.filename = filename
        self.type = IMAGE_TYPES[0][0][0]

    def create_as_full(self, filename, path, _type, description):
        self.filename = filename
        self.path = path
        self.type = _type
        self.description = description

    def __str__(self):
        if SHOW_IDS:
            return "[{}] {}".format(self.pk, self.filename)
        return self.filename
