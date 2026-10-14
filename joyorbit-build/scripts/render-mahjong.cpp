#include <QGuiApplication>
#include <QImage>
#include <QPainter>
#include <QSvgRenderer>
#include <QStringList>
int main(int argc, char** argv) {
    QGuiApplication app(argc, argv);
    if (argc != 3) return 2;
    QSvgRenderer renderer(QString::fromLocal8Bit(argv[1]));
    if (!renderer.isValid()) return 3;
    QStringList ids;
    ids << "TILE_1";
    for (const auto& group : {"CHARACTER", "BAMBOO", "ROD", "WIND", "DRAGON", "FLOWER", "SEASON"}) {
        int count = QString(group)=="DRAGON"?3:(QString(group)=="CHARACTER" || QString(group)=="BAMBOO" || QString(group)=="ROD")?9:4;
        for (int i=1;i<=count;i++) ids << QString("%1_%2").arg(group).arg(i);
    }
    QImage atlas(8*96,6*128,QImage::Format_ARGB32_Premultiplied);
    atlas.fill(Qt::transparent);
    QPainter painter(&atlas);
    painter.setRenderHint(QPainter::Antialiasing);
    for (int i=0;i<ids.size();i++) {
        if (!renderer.elementExists(ids[i])) return 4;
        renderer.render(&painter,ids[i],QRectF((i%8)*96,(i/8)*128,96,128));
    }
    painter.end();
    return atlas.save(QString::fromLocal8Bit(argv[2]))?0:5;
}
